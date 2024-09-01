from fasthtml.common import fast_app, Div, serve, Button, cookie, H1
from wordle.tw import Tailwind
from wordle.game import Eval, Game, State


app, rt = fast_app(hdrs=[Tailwind("./").run().get_link_tag()], pico=False, static_path="./")


@rt("/")
def get(data: str = None):
    return make_app(Game.from_str(data))


@rt("/new")
def post():
    return make_app(Game.from_str(None))


def make_app(g: "Game"):
    return cookie("data", g.to_str()), Div(
        Div(
            H1(Button("WORDLE", hx_post="/new"), cls="text-3xl font-bold"),
            cls="w-full flex flex-row place-content-center text-black",
        ),
        Div(
            *(make_square(g, i) for i in range(30)),
            cls="grid grid-cols-5 w-fit gap-1",
        ),
        Div(
            make_status(g),
            *(
                Div(*(make_key(g, k) for k in line), cls="my-0.5 flex w-fit gap-1")
                for line in KEYBOARD
            ),
            cls="flex flex-col place-items-center",
        ),
        cls="flex flex-col items-center gap-y-6",
        hx_swap_oob="true",
        id="app",
    )


@rt("/keypress")
def put(key: str, data: str = None):
    g = Game.from_str(data)
    squares, keys = g.keypress(key)
    return (
        cookie("data", g.to_str()),
        *[make_square(g, i) for i in squares],
        *[make_key(g, k) for k in keys],
        make_status(g),
    )


def make_status(g: "Game"):
    msgs = {State.WIN: "You win", State.LOSE: "You lose"}
    return Div(
        msgs.get(g.state),
        cls=" grid place-items-center h-8 font-bold",
        id="status",
        hx_swap_oob="true",
    )


def make_square(g: "Game", i):
    cls = "grid h-12 w-12 sm:h-14 sm:w-14 place-items-center rounded-sm text-2xl font-bold"
    c, state = g.get_square_state(i)
    styles = {
        Eval.CORRECT: f"{GREEN} text-white",
        Eval.EXIST: f"{YELLOW} text-white",
        Eval.WRONG: f"{GRAY} text-white",
        Eval.UNK: "text-black border-2 border-gray-300",
        Eval.EMPTY: "text-black border-2 border-gray-300",
    }
    return Div(c, cls=cls + " " + styles[state], id=f"sq{i}", hx_swap_oob="true")


def make_key(g: "Game", key: str):
    state = g.get_keyboard_state(key)
    cls = "grid h-14 cursor-pointer items-center rounded font-semibold"
    size = " p-2 sm:p-4 " if key == "ENTER" else " w-7 sm:w-10 "
    styles = {
        Eval.CORRECT: GREEN,
        Eval.EXIST: YELLOW,
        Eval.WRONG: GRAY,
        Eval.UNK: "bg-gray-200 hover:bg-gray-300",
    }
    kwargs = dict(id=f"kb_{key}", cls=cls + size + styles[state], hx_swap_oob="true")
    if state != Eval.WRONG:
        kwargs.update(hx_put=f"/keypress?key={key}", hx_swap="none")

    return Button(key, **kwargs)


GREEN, YELLOW, GRAY = "bg-[#20AA57]", "bg-[#E5B22D]", "bg-[#989898]"
KEYBOARD = [list("QWERTYUIOP"), list("ASDFGHJKL"), ["ENTER"] + list("ZXCVBNM") + ["DEL"]]

serve(reload_excludes=["public/app.css"])
