from colorama import Fore, Style, init

from sweeper.config import load_credentials
from sweeper.db import (
    get_connection,
    list_actionable,
    list_senders,
    set_status
)
from sweeper.sweep import run
from sweeper.unsubscribe import unsubscribe


init(autoreset=True)

RESET = Style.RESET_ALL
BOLD = Style.BRIGHT
DIM = Style.DIM

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
MAGENTA = Fore.MAGENTA
CYAN = Fore.CYAN


def clear():
    print("\033[2J\033[H", end="")


def color_status(status):
    if status == "success":
        return f"{GREEN}{status}{RESET}"

    if status == "failed":
        return f"{RED}{status}{RESET}"

    return f"{YELLOW}{status}{RESET}"


def color_method(method):
    if method == "one_click_post":
        return f"{GREEN}{method}{RESET}"

    if method == "https_link":
        return f"{CYAN}{method}{RESET}"

    if method == "mailto":
        return f"{MAGENTA}{method}{RESET}"

    return f"{DIM}{method}{RESET}"


def shorten(value, length=65):
    if not value:
        return "-"

    if len(value) <= length:
        return value

    return value[:length - 3] + "..."


def get_number(prompt, default, minimum=0):
    while True:
        value = input(
            f"{CYAN}{prompt}{RESET}"
        ).strip()

        if not value:
            return default

        try:
            value = int(value)

            if value < minimum:
                print(
                    f"{RED}enter a number >= {minimum}{RESET}"
                )
                continue

            return value

        except ValueError:
            print(
                f"{RED}enter a valid number{RESET}"
            )


def show_all_senders(db):
    rows = list_senders(db)

    print()
    print(
        f"{BOLD}{BLUE}━━━ ALL SENDERS ━━━{RESET}"
    )
    print()

    if not rows:
        print(f"{DIM}no senders stored{RESET}")
        return

    for index, row in enumerate(rows, 1):
        name = row["display_name"] or row["email"]

        print(
            f"{BLUE}[{index:02}]{RESET} "
            f"{BOLD}{name}{RESET}"
        )

        print(
            f"    {DIM}email{RESET}    {row['email']}"
        )

        print(
            f"    {DIM}messages{RESET} {row['message_count']}"
        )

        print(
            f"    {DIM}method{RESET}   "
            f"{color_method(row['unsub_method'])}"
        )

        print(
            f"    {DIM}status{RESET}   "
            f"{color_status(row['status'])}"
        )

        print()


def show_actionable(rows):
    print()
    print(
        f"{BOLD}{GREEN}━━━ READY TO UNSUBSCRIBE ━━━{RESET}"
    )
    print()

    if not rows:
        print(
            f"{GREEN}no actionable senders{RESET}"
        )
        return

    for index, row in enumerate(rows, 1):
        name = row["display_name"] or row["email"]
        target = row["https_url"] or row["mailto_url"]

        print(
            f"{GREEN}[{index:02}]{RESET} "
            f"{BOLD}{name}{RESET}"
        )

        print(
            f"    {DIM}email{RESET}    {row['email']}"
        )

        print(
            f"    {DIM}messages{RESET} {row['message_count']}"
        )

        print(
            f"    {DIM}method{RESET}   "
            f"{color_method(row['unsub_method'])}"
        )

        print(
            f"    {DIM}target{RESET}   "
            f"{shorten(target)}"
        )

        print(
            f"    {DIM}status{RESET}   "
            f"{color_status(row['status'])}"
        )

        print()


def parse_selection(value, count):
    value = value.strip().lower()

    if value == "all":
        if count == 0:
            raise ValueError("no actionable senders")

        return list(range(count))

    parts = value.split(",")
    selected = []

    for part in parts:
        part = part.strip()

        if not part:
            continue

        if "-" in part:
            values = part.split("-", 1)

            if len(values) != 2:
                raise ValueError("invalid range")

            start, end = values

            try:
                start = int(start)
                end = int(end)
            except ValueError:
                raise ValueError("invalid range")

            if start < 1 or end > count or start > end:
                raise ValueError("selection out of range")

            for number in range(start, end + 1):
                index = number - 1

                if index not in selected:
                    selected.append(index)

            continue

        try:
            number = int(part)
        except ValueError:
            raise ValueError("unknown command")

        if number < 1 or number > count:
            raise ValueError("selection out of range")

        index = number - 1

        if index not in selected:
            selected.append(index)

    if not selected:
        raise ValueError("no sender selected")

    return selected


def scan(credentials):
    print()
    print(
        f"{BOLD}{CYAN}━━━ SCAN SETTINGS ━━━{RESET}"
    )
    print()

    days = get_number(
        "days back [30]: ",
        30,
        1
    )

    limit = get_number(
        "max messages [50, 0 = all]: ",
        50,
        0
    )

    if limit == 0:
        limit = None

    print()
    print(
        f"{CYAN}scanning the last {days} days",
        end=""
    )

    if limit:
        print(f", max {limit} messages{RESET}")
    else:
        print(f", no message limit{RESET}")

    print()

    return run(
        days=days,
        limit=limit,
        credentials=credentials
    )


def unsubscribe_selected(db, rows, selected, credentials):
    print()
    print(
        f"{BOLD}{MAGENTA}━━━ SELECTED ━━━{RESET}"
    )
    print()

    for index in selected:
        row = rows[index]

        print(
            f"{CYAN}•{RESET} "
            f"{BOLD}{row['display_name'] or row['email']}{RESET} "
            f"{DIM}({row['message_count']} messages, "
            f"{row['unsub_method']}){RESET}"
        )

    print()

    confirm = input(
        f"{YELLOW}unsubscribe from all selected senders? [y/N]: {RESET}"
    ).strip().lower()

    if confirm != "y":
        print(f"{YELLOW}cancelled{RESET}")
        return

    for index in selected:
        row = rows[index]

        print()
        print(
            f"{CYAN}unsubscribing from "
            f"{row['display_name'] or row['email']}...{RESET}"
        )

        try:
            status, target = unsubscribe(
                row["unsub_method"],
                row["https_url"],
                row["mailto_url"],
                credentials["address"],
                credentials["app_password"]
            )

            set_status(
                db,
                row["email"],
                "success"
            )

            print(
                f"{GREEN}✓ success ({status}){RESET}"
            )

        except Exception as error:
            set_status(
                db,
                row["email"],
                "failed",
                str(error)
            )

            print(
                f"{RED}✗ failed: {error}{RESET}"
            )

    print()
    input(
        f"{DIM}press Enter to continue...{RESET}"
    )


def main():
    db = None

    try:
        credentials = load_credentials()
        db = get_connection()

        scan(credentials)

        while True:
            clear()

            show_all_senders(db)

            rows = list_actionable(db)
            show_actionable(rows)

            print(
                f"{BOLD}{BLUE}━━━ COMMANDS ━━━{RESET}"
            )
            print()
            print(
                f"{GREEN}1{RESET} / "
                f"{GREEN}1,3,5{RESET} / "
                f"{GREEN}1-5{RESET}   "
                f"unsubscribe selected"
            )
            print(
                f"{GREEN}all{RESET}          "
                f"unsubscribe all"
            )
            print(
                f"{CYAN}r{RESET}             "
                f"rescan inbox"
            )
            print(
                f"{RED}q{RESET}             "
                f"quit"
            )
            print()

            choice = input(
                f"{BOLD}{CYAN}>{RESET} "
            ).strip().lower()

            if choice == "q":
                break

            if choice == "r":
                scan(credentials)
                input(
                    f"{DIM}press Enter to continue...{RESET}"
                )
                continue

            try:
                selected = parse_selection(
                    choice,
                    len(rows)
                )

                unsubscribe_selected(
                    db,
                    rows,
                    selected,
                    credentials
                )

            except ValueError as error:
                print(
                    f"{RED}error: {error}{RESET}"
                )
                input(
                    f"{DIM}press Enter to continue...{RESET}"
                )

    except KeyboardInterrupt:
        print(
            f"\n{YELLOW}bye{RESET}"
        )

    finally:
        if db:
            db.close()


if __name__ == "__main__":
    main()