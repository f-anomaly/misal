import tkinter as tk
import ast
import operator as op

allowed_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.UAdd: lambda x: x,
    ast.USub: op.neg,
}

def safe_eval(expr: str):
    """
    Evaluasi ekspresi aritmatika secara aman (tanpa eval bawaan).
    Mengangkat ValueError untuk input yang tidak valid.
    """
    try:
        node = ast.parse(expr, mode='eval').body
    except Exception as e:
        raise ValueError("Sintaks tidak valid") from e

    def _eval(node):
        if isinstance(node, ast.BinOp):
            if type(node.op) not in allowed_operators:
                raise ValueError("Operator tidak diizinkan")
            left = _eval(node.left)
            right = _eval(node.right)
            return allowed_operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in allowed_operators:
                raise ValueError("Operator unary tidak diizinkan")
            operand = _eval(node.operand)
            return allowed_operators[type(node.op)](operand)
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            else:
                raise ValueError("Hanya angka yang diizinkan")
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Expr):
            return _eval(node.value)
        else:
            raise ValueError("Ekspresi tidak diizinkan")

    result = _eval(node)
    return result


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Python (GUI)")
        self.resizable(False, False)
        self.geometry("320x420")
        self.config(padx=10, pady=10)
        self.expression = ""
        self.create_widgets()

    def create_widgets(self):
        # Display
        self.display_var = tk.StringVar(value="0")
        display = tk.Entry(self, textvariable=self.display_var, font=("Helvetica", 20), bd=5, relief=tk.RIDGE, justify='right')
        display.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=(0,10))
        display.bind("<Key>", lambda e: "break")  # cegah editing langsung pada Entry

        # Tombol-tombol
        buttons = [
            ('C', 1, 0, self.clear),
            ('←', 1, 1, self.backspace),
            ('%', 1, 2, lambda: self.append('%')),
            ('/', 1, 3, lambda: self.append('/')),
            ('7', 2, 0, lambda: self.append('7')),
            ('8', 2, 1, lambda: self.append('8')),
            ('9', 2, 2, lambda: self.append('9')),
            ('*', 2, 3, lambda: self.append('*')),
            ('4', 3, 0, lambda: self.append('4')),
            ('5', 3, 1, lambda: self.append('5')),
            ('6', 3, 2, lambda: self.append('6')),
            ('-', 3, 3, lambda: self.append('-')),
            ('1', 4, 0, lambda: self.append('1')),
            ('2', 4, 1, lambda: self.append('2')),
            ('3', 4, 2, lambda: self.append('3')),
            ('+', 4, 3, lambda: self.append('+')),
            ('±', 5, 0, self.negate),
            ('0', 5, 1, lambda: self.append('0')),
            ('.', 5, 2, lambda: self.append('.')),
            ('=', 5, 3, self.calculate),
        ]

        for (text, r, c, cmd) in buttons:
            btn = tk.Button(self, text=text, width=6, height=2, font=("Helvetica", 14), command=cmd)
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        # atur grid weights agar tombol meregang rapi
        for i in range(6):
            self.rowconfigure(i, weight=1)
        for j in range(4):
            self.columnconfigure(j, weight=1)

        # Binding keyboard
        self.bind_all("<Key>", self.on_keypress)
        self.bind_all("<Return>", lambda e: self.calculate())
        self.bind_all("<BackSpace>", lambda e: self.backspace())
        self.bind_all("<Escape>", lambda e: self.clear())

    def append(self, char):
        # cegah dua titik berturut-turut di satu angka sederhana
        if char == '.' and self.expression and self.expression.split()[-1].count('.') >= 1:
            last = self.expression.rstrip()
            if last and (last[-1].isdigit() or last[-1] == '.'):
                seg = ''
                for ch in reversed(last):
                    if ch.isdigit() or ch == '.':
                        seg = ch + seg
                    else:
                        break
                if '.' in seg:
                    return

        self.expression += str(char)
        self._update_display()

    def clear(self):
        self.expression = ""
        self._update_display()

    def backspace(self):
        if self.expression:
            self.expression = self.expression[:-1]
        self._update_display()

    def negate(self):
        # tambahkan unary minus ke awal ekspresi jika kosong, atau bungkus ekspresi menjadi negatif
        if not self.expression:
            self.expression = "-"
        else:
            last_char = self.expression[-1]
            if last_char.isdigit() or last_char == '.':
                self.expression = f"({self.expression})*(-1)"
            else:
                self.expression += '-'
        self._update_display()

    def calculate(self):
        if not self.expression:
            return
        expr = self.expression.replace('×', '*').replace('÷', '/')
        try:
            result = safe_eval(expr)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression = str(result)
        except Exception as e:
            self.expression = "Error"
        self._update_display()

    def _update_display(self):
        if not self.expression:
            self.display_var.set("0")
        else:
            self.display_var.set(self.expression)

    def on_keypress(self, event):
        # terima angka, operator, titik, percent
        allowed_keys = "0123456789+-*/().%"
        if event.char in allowed_keys:
            self.append(event.char)
        elif event.keysym == "Return":
            self.calculate()
        elif event.keysym == "BackSpace":
            self.backspace()
        elif event.keysym == "Escape":
            self.clear()


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
