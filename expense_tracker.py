"""Personal expense tracker with CSV storage."""

import csv
import os
import sys
from datetime import datetime

DATA_FILE = "expenses.csv"
DATE_FORMAT = "%d-%m-%Y"
CSV_HEADERS = ["id", "title", "amount", "category", "date"]
STARTING_ID = 101
CURRENCY = "\u20b9"
BOX_WIDTH = 80
USE_COLOR = True


class UI:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"

    _color_ready = False

    @classmethod
    def init(cls):
        if not USE_COLOR:
            cls._color_ready = False
            return
        if os.name == "nt":
            os.system("")
        cls._color_ready = sys.stdout.isatty() or os.name == "nt"

    @classmethod
    def c(cls, text, *codes):
        if not (USE_COLOR and cls._color_ready):
            return text
        return "".join(codes) + text + cls.RESET

    @staticmethod
    def visible_len(text):
        out, i = 0, 0
        while i < len(text):
            if text[i] == "\033":
                while i < len(text) and text[i] != "m":
                    i += 1
                i += 1
            else:
                out += 1
                i += 1
        return out

    @staticmethod
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def pause():
        try:
            input(UI.c("\n  Press Enter to return to the main menu...", UI.DIM))
        except (EOFError, KeyboardInterrupt):
            pass

    @classmethod
    def top(cls, color=None):
        color = color or cls.CYAN
        print(cls.c("\u2554" + "\u2550" * (BOX_WIDTH - 2) + "\u2557", color))

    @classmethod
    def bottom(cls, color=None):
        color = color or cls.CYAN
        print(cls.c("\u255a" + "\u2550" * (BOX_WIDTH - 2) + "\u255d", color))

    @classmethod
    def divider(cls, color=None):
        color = color or cls.CYAN
        print(cls.c("\u2560" + "\u2550" * (BOX_WIDTH - 2) + "\u2563", color))

    @classmethod
    def row(cls, text="", align="left", color=None):
        frame = cls.c("\u2551", color or cls.CYAN)
        pad = max(BOX_WIDTH - 4 - cls.visible_len(text), 0)
        if align == "center":
            left = pad // 2
            body = " " * left + text + " " * (pad - left)
        elif align == "right":
            body = " " * pad + text
        else:
            body = text + " " * pad
        print(f"{frame} {body} {frame}")

    @classmethod
    def panel(cls, title, lines, color=None):
        color = color or cls.CYAN
        cls.top(color)
        cls.row(cls.c(title.upper(), cls.BOLD, color), "center", color)
        cls.divider(color)
        for line in lines:
            cls.row(line, color=color)
        cls.bottom(color)

    @classmethod
    def header(cls, title, subtitle=""):
        cls.top()
        cls.row(cls.c(title.upper(), cls.BOLD, cls.WHITE), "center")
        if subtitle:
            cls.row(cls.c(subtitle, cls.DIM), "center")
        cls.bottom()

    @classmethod
    def success(cls, message):
        print(cls.c(f"  [OK]      {message}", cls.GREEN, cls.BOLD))

    @classmethod
    def error(cls, message):
        print(cls.c(f"  [ERROR]   {message}", cls.RED, cls.BOLD))

    @classmethod
    def info(cls, message):
        print(cls.c(f"  [INFO]    {message}", cls.BLUE))

    @classmethod
    def system(cls, message):
        print(cls.c(f"  [SYSTEM]  {message}", cls.MAGENTA))

    @classmethod
    def warn(cls, message):
        print(cls.c(f"  [WARNING] {message}", cls.YELLOW))

    COLS = [("ID", 6), ("TITLE", 26), ("AMOUNT", 15),
            ("CATEGORY", 15), ("DATE", 12)]

    @classmethod
    def _rule(cls, left, mid, right):
        parts = ["\u2500" * width for _, width in cls.COLS]
        return cls.c(left + mid.join(parts) + right, cls.DIM)

    @classmethod
    def table(cls, expenses, footer=True):
        v = cls.c("\u2502", cls.DIM)

        print(cls._rule("\u250c", "\u252c", "\u2510"))
        head = v.join(
            cls.c(f" {name:<{width - 2}} ", cls.BOLD, cls.WHITE)
            for name, width in cls.COLS
        )
        print(f"{v}{head}{v}")
        print(cls._rule("\u251c", "\u253c", "\u2524"))

        for expense in expenses:
            cells = [
                cls.c(f" {expense.id:<4} ", cls.YELLOW),
                f" {expense.title[:24]:<24} ",
                cls.c(f" {CURRENCY}{expense.amount:>12,.2f} ", cls.GREEN),
                cls.c(f" {expense.category[:13]:<13} ", cls.MAGENTA),
                cls.c(f" {expense.date:<10} ", cls.DIM),
            ]
            print(f"{v}{v.join(cells)}{v}")

        print(cls._rule("\u2514", "\u2534", "\u2518"))

        if footer:
            total = sum(e.amount for e in expenses)
            label = cls.c(f"  {len(expenses)} record(s) shown", cls.DIM)
            value = cls.c(f"Subtotal: {CURRENCY}{total:,.2f}",
                          cls.GREEN, cls.BOLD)
            print(f"{label}   |   {value}\n")

    @classmethod
    def bar(cls, share, width=34):
        filled = int(round(share / 100 * width))
        return (cls.c("\u2588" * filled, cls.GREEN) +
                cls.c("\u2591" * (width - filled), cls.DIM))


class Expense:

    def __init__(self, expense_id, title, amount, category, date):
        self.id = int(expense_id)
        self.title = str(title).strip()
        self.amount = float(amount)
        self.category = str(category).strip().title()
        self.date = str(date).strip()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "amount": f"{self.amount:.2f}",
            "category": self.category,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, row):
        return cls(
            expense_id=row["id"],
            title=row["title"],
            amount=row["amount"],
            category=row["category"],
            date=row["date"],
        )

    def as_date(self):
        try:
            return datetime.strptime(self.date, DATE_FORMAT)
        except ValueError:
            return None


class ExpenseTracker:

    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.expenses = []
        self._next_id = STARTING_ID

    def generate_id(self):
        used = {e.id for e in self.expenses}
        while self._next_id in used:
            self._next_id += 1
        return self._next_id

    def add_expense(self, title, amount, category, date):
        expense = Expense(self.generate_id(), title, amount, category, date)
        self.expenses.append(expense)
        self._next_id += 1
        return expense

    def get_all(self):
        return list(self.expenses)

    def is_empty(self):
        return not self.expenses

    def find_by_id(self, expense_id):
        for expense in self.expenses:
            if expense.id == expense_id:
                return expense
        return None

    def search_by_keyword(self, keyword):
        key = keyword.strip().lower()
        return [e for e in self.expenses
                if key in e.title.lower() or key in e.category.lower()]

    def update_expense(self, expense_id, title=None, amount=None,
                       category=None, date=None):
        expense = self.find_by_id(expense_id)
        if expense is None:
            return None
        if title:
            expense.title = title.strip()
        if amount is not None:
            expense.amount = float(amount)
        if category:
            expense.category = category.strip().title()
        if date:
            expense.date = date.strip()
        return expense

    def delete_expense(self, expense_id):
        expense = self.find_by_id(expense_id)
        if expense is None:
            return None
        self.expenses.remove(expense)
        return expense

    def grand_total(self):
        return sum(e.amount for e in self.expenses)

    def count(self):
        return len(self.expenses)

    def category_totals(self):
        totals = {}
        for e in self.expenses:
            totals[e.category] = totals.get(e.category, 0.0) + e.amount
        return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))

    def monthly_totals(self):
        buckets = {}
        for e in self.expenses:
            parsed = e.as_date()
            if parsed is None:
                continue
            key = parsed.strftime("%m-%Y")
            buckets[key] = buckets.get(key, 0.0) + e.amount
        return dict(sorted(
            buckets.items(),
            key=lambda kv: datetime.strptime(kv[0], "%m-%Y")))

    def largest_expense(self):
        if not self.expenses:
            return None
        return max(self.expenses, key=lambda e: e.amount)

    def smallest_expense(self):
        if not self.expenses:
            return None
        return min(self.expenses, key=lambda e: e.amount)

    def average_expense(self):
        return self.grand_total() / self.count() if self.expenses else 0.0

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return 0, 0

        loaded, skipped = 0, 0
        try:
            with open(self.filename, "r", newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    try:
                        expense = Expense.from_dict(row)
                    except (ValueError, TypeError, KeyError):
                        skipped += 1
                        continue
                    if self.find_by_id(expense.id):
                        skipped += 1
                        continue
                    self.expenses.append(expense)
                    loaded += 1
        except (OSError, csv.Error) as exc:
            UI.warn(f"Could not read data file ({exc}).")
            return 0, 0

        if self.expenses:
            self._next_id = max(e.id for e in self.expenses) + 1
        return loaded, skipped

    def save_to_file(self):
        try:
            with open(self.filename, "w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS)
                writer.writeheader()
                for expense in self.expenses:
                    writer.writerow(expense.to_dict())
            return True
        except OSError as exc:
            UI.error(f"Failed to write data file ({exc}).")
            return False


class ExpenseCLI:

    MENU = [
        ("1", "Add New Expense", "Record a new transaction"),
        ("2", "View All Expenses", "Browse all records"),
        ("3", "Search Expense", "Find records by ID or keyword"),
        ("4", "Update Expense", "Edit an existing entry"),
        ("5", "Delete Expense", "Remove a record"),
        ("6", "View Summary", "Totals and category breakdown"),
        ("7", "Exit & Save Data", "Write to disk and close"),
    ]

    def __init__(self, tracker):
        self.tracker = tracker

    @staticmethod
    def ask(label):
        return input(UI.c("  > ", UI.CYAN, UI.BOLD) + label)

    @classmethod
    def prompt_text(cls, message, allow_blank=False, default=None):
        while True:
            value = cls.ask(message).strip()
            if value:
                return value
            if allow_blank:
                return default
            UI.error("This field cannot be empty.")

    @classmethod
    def prompt_amount(cls, message, allow_blank=False):
        while True:
            raw = cls.ask(message).strip().replace(",", "")
            if not raw and allow_blank:
                return None
            try:
                value = float(raw)
            except ValueError:
                UI.error("Please enter a number.")
                continue
            if value <= 0:
                UI.error("Amount must be greater than zero.")
                continue
            if value > 1_000_000_000:
                UI.error("Amount is too large. Please re-check.")
                continue
            return round(value, 2)

    @classmethod
    def prompt_int(cls, message):
        while True:
            raw = cls.ask(message).strip()
            try:
                return int(raw)
            except ValueError:
                UI.error("Please enter a whole number.")

    @classmethod
    def prompt_date(cls, message, allow_blank=True, default=None):
        while True:
            raw = cls.ask(message).strip()
            if not raw:
                if default is not None:
                    return default
                if allow_blank:
                    today = datetime.now().strftime(DATE_FORMAT)
                    UI.system(f"No date entered. Using today: {today}")
                    return today
            try:
                parsed = datetime.strptime(raw, DATE_FORMAT)
            except ValueError:
                UI.error("Date must be DD-MM-YYYY (e.g. 09-03-2026).")
                continue
            if parsed > datetime.now():
                UI.error("Future dates are not allowed.")
                continue
            return parsed.strftime(DATE_FORMAT)

    @classmethod
    def confirm(cls, message):
        answer = cls.ask(f"{message} (y/n): ").strip().lower()
        return answer in ("y", "yes")

    def dashboard_strip(self):
        total = self.tracker.grand_total()
        count = self.tracker.count()
        cats = len(self.tracker.category_totals())
        avg = self.tracker.average_expense()

        def stat(label, value, color):
            return UI.c(f"{label}: ", UI.DIM) + UI.c(value, color, UI.BOLD)

        UI.row(
            stat("Records", f"{count}", UI.YELLOW) + "   " +
            stat("Total", f"{CURRENCY}{total:,.2f}", UI.GREEN) + "   " +
            stat("Categories", f"{cats}", UI.MAGENTA) + "   " +
            stat("Avg", f"{CURRENCY}{avg:,.2f}", UI.BLUE),
            "center")

    def show_menu(self):
        UI.clear()
        UI.top()
        UI.row(UI.c("PERSONAL EXPENSE TRACKER", UI.BOLD, UI.WHITE), "center")
        UI.divider()
        self.dashboard_strip()
        UI.divider()
        UI.row()
        for key, name, hint in self.MENU:
            bullet = UI.c(f"[{key}]", UI.YELLOW, UI.BOLD)
            label = UI.c(f"{name:<24}", UI.WHITE)
            note = UI.c(hint, UI.DIM)
            UI.row(f"  {bullet}  {label}{note}")
        UI.row()
        UI.bottom()

    def add_expense(self):
        UI.clear()
        UI.header("Add New Expense", "Fill in the details below")
        print()

        title = self.prompt_text("Enter Expense Title: ")
        amount = self.prompt_amount("Enter Expense Amount: ")
        category = self.prompt_text("Enter Expense Category: ")
        date = self.prompt_date(
            "Enter Expense Date (DD-MM-YYYY) or leave blank for today: ")

        expense = self.tracker.add_expense(title, amount, category, date)
        print()
        UI.success(f"Expense added with ID {expense.id}.")
        print()
        UI.table([expense], footer=False)

    def view_expenses(self):
        UI.clear()
        UI.header("All Expenses")
        print()

        if self.tracker.is_empty():
            UI.info("No expenses yet. Add one first (Option 1).")
            return

        print(UI.c("  Sort by:  [1] ID   [2] Amount (high to low)   "
                   "[3] Date   [4] Category", UI.DIM))
        choice = self.prompt_text("Choose sort order (blank = ID): ",
                                  allow_blank=True, default="1")

        expenses = self.tracker.get_all()
        if choice == "2":
            expenses.sort(key=lambda e: e.amount, reverse=True)
        elif choice == "3":
            expenses.sort(key=lambda e: e.as_date() or datetime.min)
        elif choice == "4":
            expenses.sort(key=lambda e: (e.category, -e.amount))
        else:
            expenses.sort(key=lambda e: e.id)

        print()
        UI.table(expenses)

    def search_expense(self):
        UI.clear()
        UI.header("Search Expense")
        print()

        if self.tracker.is_empty():
            UI.info("Nothing to search. No expenses yet.")
            return

        print(UI.c("  [1] Search by ID", UI.WHITE))
        print(UI.c("  [2] Search by keyword (title or category)", UI.WHITE))
        print()
        mode = self.prompt_text("Choose search mode (1-2): ")

        if mode == "1":
            expense_id = self.prompt_int("Enter Expense ID to search: ")
            found = self.tracker.find_by_id(expense_id)
            if found is None:
                print()
                UI.error(f"No record with ID {expense_id}.")
                return
            print()
            UI.table([found], footer=False)

        elif mode == "2":
            keyword = self.prompt_text("Enter keyword: ")
            results = self.tracker.search_by_keyword(keyword)
            if not results:
                print()
                UI.error(f"No records matched '{keyword}'.")
                return
            print()
            UI.success(f"{len(results)} record(s) found.")
            print()
            UI.table(results)

        else:
            print()
            UI.error("Invalid search mode.")

    def update_expense(self):
        UI.clear()
        UI.header("Update Expense")
        print()

        if self.tracker.is_empty():
            UI.info("Nothing to update. No expenses yet.")
            return

        expense_id = self.prompt_int("Enter Expense ID to update: ")
        expense = self.tracker.find_by_id(expense_id)
        if expense is None:
            print()
            UI.error(f"No record with ID {expense_id}.")
            return

        print()
        UI.table([expense], footer=False)
        UI.warn("Press Enter on any field to keep its existing value.")
        print()

        title = self.prompt_text(
            f"New Title [{expense.title}]: ", allow_blank=True)
        amount = self.prompt_amount(
            f"New Amount [{expense.amount:.2f}]: ", allow_blank=True)
        category = self.prompt_text(
            f"New Category [{expense.category}]: ", allow_blank=True)
        date = self.prompt_date(
            f"New Date (DD-MM-YYYY) [{expense.date}]: ", default=expense.date)

        self.tracker.update_expense(expense_id, title, amount, category, date)
        print()
        UI.success(f"Record ID {expense_id} updated.")
        print()
        UI.table([expense], footer=False)

    def delete_expense(self):
        UI.clear()
        UI.header("Delete Expense")
        print()

        if self.tracker.is_empty():
            UI.info("Nothing to delete. No expenses yet.")
            return

        expense_id = self.prompt_int("Enter Expense ID to delete: ")
        expense = self.tracker.find_by_id(expense_id)
        if expense is None:
            print()
            UI.error(f"No record with ID {expense_id}.")
            return

        print()
        UI.table([expense], footer=False)

        if not self.confirm("Delete this record?"):
            print()
            UI.info("Deletion cancelled.")
            return

        self.tracker.delete_expense(expense_id)
        print()
        UI.success(f"Record ID {expense_id} deleted.")

    def view_summary(self):
        UI.clear()
        UI.header("Summary")
        print()

        if self.tracker.is_empty():
            UI.info("No data yet. Add expenses first.")
            return

        total = self.tracker.grand_total()
        biggest = self.tracker.largest_expense()
        smallest = self.tracker.smallest_expense()

        def metric(label, value):
            return (UI.c(f"{label:<36}", UI.WHITE) +
                    UI.c(": ", UI.DIM) + UI.c(value, UI.GREEN, UI.BOLD))

        UI.panel("Overview", [
            metric("Total Spent", f"{CURRENCY}{total:,.2f}"),
            metric("Number of Records", f"{self.tracker.count()}"),
            metric("Average per Expense",
                   f"{CURRENCY}{self.tracker.average_expense():,.2f}"),
            metric("Highest Expense",
                   f"{CURRENCY}{biggest.amount:,.2f}  ({biggest.title})"),
            metric("Lowest Expense",
                   f"{CURRENCY}{smallest.amount:,.2f}  ({smallest.title})"),
            metric("Categories",
                   f"{len(self.tracker.category_totals())}"),
        ])
        print()

        categories = self.tracker.category_totals()
        width = max(len(name) for name in categories)
        lines = []
        for name, amount in categories.items():
            share = (amount / total) * 100 if total else 0
            lines.append(
                UI.c(f"{name:<{width}}", UI.MAGENTA) + "  " +
                UI.bar(share, 30) + "  " +
                UI.c(f"{CURRENCY}{amount:>10,.2f}", UI.GREEN) +
                UI.c(f"  {share:5.1f}%", UI.DIM))
        UI.panel("Category Breakdown", lines, UI.MAGENTA)
        print()

        months = self.tracker.monthly_totals()
        if months:
            peak = max(months.values())
            lines = []
            for month, amount in months.items():
                share = (amount / peak) * 100 if peak else 0
                lines.append(
                    UI.c(f"{month:<7}", UI.YELLOW) + "  " +
                    UI.bar(share, 30) + "  " +
                    UI.c(f"{CURRENCY}{amount:>10,.2f}", UI.GREEN))
            UI.panel("Monthly Totals", lines, UI.YELLOW)

    def exit_and_save(self):
        UI.clear()
        UI.header("Saving")
        print()
        if self.tracker.save_to_file():
            UI.success(f"{self.tracker.count()} record(s) saved to "
                       f"'{self.tracker.filename}'.")
        else:
            UI.warn("Data may not have been saved correctly.")
        print()

    def splash(self):
        loaded, skipped = self.tracker.load_from_file()
        UI.clear()
        UI.top()
        UI.row()
        UI.row(UI.c("PERSONAL EXPENSE TRACKER", UI.BOLD, UI.WHITE), "center")
        UI.row()
        UI.divider()
        if loaded:
            UI.row(UI.c(f"  {loaded} record(s) loaded from "
                        f"'{self.tracker.filename}'", UI.GREEN))
        else:
            UI.row(UI.c("  No previous data found. Starting empty.",
                        UI.YELLOW))
        if skipped:
            UI.row(UI.c(f"  {skipped} bad/duplicate row(s) skipped", UI.RED))
        UI.row(UI.c(f"  Started {datetime.now():%d-%m-%Y at %H:%M}", UI.DIM))
        UI.bottom()
        UI.pause()

    def run(self):
        UI.init()
        self.splash()

        actions = {
            "1": self.add_expense,
            "2": self.view_expenses,
            "3": self.search_expense,
            "4": self.update_expense,
            "5": self.delete_expense,
            "6": self.view_summary,
        }

        while True:
            self.show_menu()
            try:
                choice = self.ask("Choose option (1-7): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                self.exit_and_save()
                break

            if choice == "7":
                self.exit_and_save()
                break

            action = actions.get(choice)
            if action is None:
                UI.error("Invalid option. Choose a number from 1 to 7.")
                UI.pause()
                continue

            try:
                action()
            except (EOFError, KeyboardInterrupt):
                print()
                self.exit_and_save()
                break
            except Exception as exc:
                print()
                UI.error(f"Something went wrong ({exc}). Returning to menu.")

            UI.pause()


def main():
    tracker = ExpenseTracker(DATA_FILE)
    ExpenseCLI(tracker).run()


if __name__ == "__main__":
    main()
