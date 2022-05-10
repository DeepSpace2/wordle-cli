#!/usr/bin/env python3

import argparse
import random

from datetime import datetime
from typing import Union

import wordle

from cli import CLIPlayer


def parse_cli_args() -> argparse.Namespace:
    def _solution_arg_verifier(solution_arg: str) -> str:
        solution_arg = solution_arg.upper()
        if not isinstance(solution_arg, str) or len(solution_arg) != game.LENGTH:
            raise argparse.ArgumentTypeError(
                f"SOLUTION argument must be a {game.LENGTH}-letter word")
        if solution_arg not in game.VALID_GUESSES:
            raise argparse.ArgumentTypeError(f"{solution_arg} is not in dict")
        return solution_arg

    def _user_specified_solution_arg(arg: str) -> Union[str, int]:
        """A user-chosen solution, whether a day number or a provided string"""
        if arg.isdigit() and int(arg) >= 0:
            # This is a user-provided game number to return
            return int(arg)
        else:
            # This is a user-provided solution to verify
            return _solution_arg_verifier(arg)

    args = argparse.ArgumentParser()
    args.add_argument("--hints",
                      action="store_true",
                      help="After each guess, report number of possible words remaining")
    args.add_argument("--today",
                      action="store_true",
                      help=argparse.SUPPRESS)
    args.add_argument("user_specified_solution",
                      type=_user_specified_solution_arg,
                      metavar="--today|DAY|SOLUTION",
                      nargs="?",
                      help=f"Use the official solution from --today, from given DAY, "
                           f"or provide a ({game.LENGTH}-letter) SOLUTION")

    namespace = args.parse_args()

    if type(namespace.user_specified_solution) == int:
        namespace.day_number = namespace.user_specified_solution
    else:
        namespace.day_number = None

    if type(namespace.user_specified_solution) == str:
        namespace.solution = namespace.user_specified_solution
    else:
        namespace.solution = None

    return namespace


def days_since_wordle_epoch():
    return (datetime.utcnow() - datetime(2021, 6, 19)).days


if __name__ == "__main__":
    game = wordle.Game()
    player = CLIPlayer()

    cli_args = None
    try:
        cli_args = parse_cli_args()
    except argparse.ArgumentTypeError as e:
        player.warn(e)
        exit(1)

    if [cli_args.today, cli_args.day_number is not None,
            cli_args.solution is not None].count(True) > 1:
        player.warn("Multiple --today|DAY|SOLUTION options provided!")

    if cli_args.today:
        game_number = days_since_wordle_epoch() % len(game.VALID_SOLUTIONS)
    elif cli_args.day_number and cli_args.day_number > 0:
        game_number = cli_args.day_number % len(game.VALID_SOLUTIONS)
    else:
        game_number = None

    if game_number:
        solution = game.VALID_SOLUTIONS[game_number]
        player.GAME_NUMBER = game_number
        player.warn(f"Game number will be {player.GAME_NUMBER}")
    elif cli_args.solution:
        solution = cli_args.solution
        player.warn(f"Solution will be {solution}")
    else:
        solution = random.choice(game.VALID_SOLUTIONS)

    while True:
        try:
            game.play(player, solution, hints=cli_args.hints)
        except (KeyboardInterrupt, EOFError):
            print()
            player.quit()

        if cli_args.solution:
            exit()

        try:
            player.again()
            print()
        except (KeyboardInterrupt, EOFError):
            print()
            exit()
