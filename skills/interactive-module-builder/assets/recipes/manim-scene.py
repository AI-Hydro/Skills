# RECIPE: Manim video cell body.
#
# Drop this into the <pre class="aihydro-source"> of a cell marked
#   data-aihydro-render="video"  (or data-language="manim").
# The kernel finds every Scene subclass, renders it to a short MP4, and the
# bridge plays it inline. Do NOT call manim from the CLI, write files, or set
# output paths — the kernel handles capture. Manim is an OPTIONAL kernel dep;
# if it is missing the cell degrades to a "Manim is not installed" note.
#
# Keep scenes short (a few seconds) and use the AI-Hydro palette.

from manim import *


class TwiScene(Scene):
    def construct(self):
        title = Text("Topographic Wetness Index", font="Poppins").scale(0.6)
        title.set_color("#7dd3fc").to_edge(UP)
        eq = MathTex(r"\mathrm{TWI} = \ln\!\left(\frac{a}{\tan\beta}\right)")
        eq.set_color("#00DDFF").scale(1.2)

        self.play(Write(title))
        self.play(Write(eq))
        self.wait(0.5)

        a_label = Text("a = upslope contributing area", font="Nunito").scale(0.4)
        b_label = Text("tan β = local slope", font="Nunito").scale(0.4)
        a_label.set_color("#94a3b8").next_to(eq, DOWN, buff=0.6)
        b_label.set_color("#94a3b8").next_to(a_label, DOWN, buff=0.2)
        self.play(FadeIn(a_label), FadeIn(b_label))
        self.wait(1)
