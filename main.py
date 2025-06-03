from manim import *

def standard_vertice(label: MathTex):
    return LabeledDot(label=label, radius=0.5, stroke_width=2, stroke_color=BLUE, fill_opacity=0)

def update_arrow(arrow:LabeledArrow, start, end):
    tip = arrow.pop_tips()[0]
    arrow.set_points_by_ends(start, end)
    arrow.add_tip(tip)
    arrow.label.move_to(arrow.get_midpoint())

def update_dot_fill(dot:LabeledDot, color, opacity):
    dot.set_fill(color, opacity)
    dot.submobjects[0].set_fill(WHITE, opacity=1)

def init_flow_net():
    # ---Init Flow_Net---
    # Creating Init Vertices
    vert_label = ["v_1", "v_2", "v_3", "v_4", "s", "t"]
    vertices = {}
    for i in vert_label:
        print(i, type(i))
        vert = standard_vertice(MathTex(i))
        vertices[i] = vert
    del vert_label

    vertices["v_1"].move_to((-2, 1.5, 0))
    vertices["v_2"].move_to((-2, -1.5, 0))
    vertices["v_3"].move_to((2, 1.5, 0))
    vertices["v_4"].move_to((2, -1.5, 0))
    vertices["t"].move_to((6, 0, 0))
    vertices["s"].move_to((-6, 0, 0))

    update_dot_fill(vertices["s"], DARK_BLUE, 1)

    # Creating Edges
    edge_label = {
        ("s", "v_1"): "16", ("s", "v_2"): "13",
        ("v_1", "v_3"): "12",
        ("v_2", "v_1"): "4", ("v_2", "v_4"): "14",\
        ("v_3", 't'): "20", ("v_3", "v_2"): "2",\
        ("v_4", "t"): "4", ("v_4", "v_3"): "7",
    }
    edges = {}
    for (u, v) in edge_label:
        edge = LabeledArrow(label=MathTex(edge_label[(u, v)]))
        update_arrow(edge, start=vertices[u], end=vertices[v])
        edges[(u, v)] = edge
    del edge_label

    return vertices, edges

def animate_flow(scene:Scene, quantity, start: LabeledDot, end: LabeledDot, capcity, used, edge):
    data: list[Square] = []
    for i in range(quantity):
        data.append(Square(side_length=0.3, color=BLUE).move_to(start))

    new_edge = LabeledArrow(label=MathTex(f"{used}/{capcity}"))
    update_arrow(new_edge, start, end)

    animations = [
        mob.animate.move_to(end)
        for mob in data
    ]

    scene.play(AnimationGroup(
        Transform(edge, new_edge),
        AnimationGroup(*animations, lag_ratio=0.3),
        )
    )
    scene.remove(*data)
    # new_edge.to_corner()
    scene.add(new_edge)
    scene.remove(edge)

    return new_edge

def animate_flow_parallel(scene:Scene, quantity, start: LabeledDot, end: LabeledDot, capcity, used, edge=None, parallel_edge=None):
    def create_parallel():
        new_parallel = LabeledArrow(label=MathTex(f"{used}"))
        update_arrow(new_parallel, end.get_corner(DL), start.get_corner(DR))
        return new_parallel

    def create_edge():
        new_edge = LabeledArrow(label=MathTex(f"{capcity - used}"))
        update_arrow(new_edge, start.get_corner(UR), end.get_corner(UL))
        return new_edge

    data: list[Square] = []
    for i in range(quantity):
        data.append(Square(side_length=0.3, color=BLUE).move_to(start))

    new_edge = None
    new_parallel = None
    # only under case used == capcity edge is not used
    if used < capcity:
        new_edge = create_edge()
    # only under case used == 0 parallel edge is not used
    if used > 0:
        new_parallel = create_parallel()

    data_animations = [
        mob.animate.move_to(end)
        for mob in data
    ]
    edge_animations = []
    new_edges = []

    for i, t in [(edge, new_edge), (parallel_edge, new_parallel)]:
        if i is None:
            edge_animations.append(Write(t))
            new_edges.append(t)
        elif t is None:
            edge_animations.append(FadeOut(i))
        else:
            edge_animations.append(Transform(i, t))
            new_edges.append(t)

    scene.play(AnimationGroup(
        *edge_animations,
        AnimationGroup(*data_animations, lag_ratio=0.3),
        )
    )
    scene.add(*new_edges)
    scene.remove(edge, parallel_edge)
    scene.remove(*data)

    return new_edge, new_parallel

class Flow_Net(Scene):
    def construct(self):
        vertices, edges = init_flow_net()

        # ---!!!Start Animations!!!---
        # ---Title---
        title = Text("流网络").scale(2)
        title.set_color(WHITE)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.scale(0.5))
        self.play(title.animate.to_edge(UP))

        # ---Show Source and Target---
        vertices["s"].move_to(LEFT*1.5)
        vertices["t"].move_to(RIGHT*1.5)

        vertices["s"].scale(2)
        vertices["t"].scale(2)

        self.play(Create(vertices["s"]), Create(vertices["t"]))

        # ---Move Source and Target to side---
        self.play(vertices["s"].animate.scale(0.5), vertices["t"].animate.scale(0.5))
        self.play(vertices["s"].animate.move_to((-6,0,0)), vertices["t"].animate.move_to((6,0,0)))

        # ---Show Flow Network---
        flow_net = VGroup(vertices.values(), edges.values())
        flow_net.remove(vertices["s"], vertices["t"])
        self.play(Write(flow_net))
        self.wait()

        # ---Show Maxmum Flow Question---
        data = []
        for i in range(5):
            data.append(Square(side_length=0.3, color=BLUE).move_to(vertices["s"]))

        self.play(
            data[0].animate.move_to(vertices["v_1"]),
            data[1].animate.move_to(vertices["v_1"]),
            data[2].animate.move_to(vertices["v_2"]),
            data[3].animate.move_to(vertices["v_2"]),
            data[4].animate.move_to(vertices["v_2"]),
        )
        self.play(
            data[0].animate.move_to(vertices["v_3"]), # v_1
            data[1].animate.move_to(vertices["v_3"]), # v_1
            data[2].animate.move_to(vertices["v_1"]), # v_2
            data[3].animate.move_to(vertices["v_4"]), # v_2
            data[4].animate.move_to(vertices["v_4"]), # v_2
        )
        self.play(
            data[0].animate.move_to(vertices["t"]), # v_3
            data[1].animate.move_to(vertices["v_2"]), # v_3
            data[2].animate.move_to(vertices["v_3"]), # v_1
            data[3].animate.move_to(vertices["v_3"]), # v_4
            data[4].animate.move_to(vertices["t"]), # v_4
        )
        self.play(
            data[1].animate.move_to(vertices["v_4"]), # v_2
            data[2].animate.move_to(vertices["t"]), # v_3
            data[3].animate.move_to(vertices["t"]), # v_3
        )
        self.play(
            data[1].animate.move_to(vertices["t"]), # v_2
        )
        self.play(FadeOut(*data))

        self.play(FadeOut(*self.mobjects))

class Residual_Net(Scene):
    def construct(self):
        # ---!!!Start Animation!!!---
        # ---Title---
        # title = Text("残留网络").scale(2)
        # title.set_color(WHITE)
        # self.play(Write(title))
        # self.wait(1)
        # self.play(title.animate.scale(0.5))
        # self.play(title.animate.to_edge(UP))

        # ---Draw a Simple Flow Net---
        source = standard_vertice(MathTex("s")).shift(LEFT*2)
        target = standard_vertice(MathTex("t")).shift(RIGHT*2)

        update_dot_fill(source, DARK_BLUE, 1)

        flow = LabeledArrow(label=MathTex("8"))
        update_arrow(flow, source, target)

        self.play(Write(source), Write(target), Write(flow))

        # ---Make Simple Residual_Net---
        res_source = source.copy()
        res_target = target.copy()
        res_flow   = flow.copy()

        flow_net = VGroup(source, target, flow)
        res_net  = VGroup(res_source, res_target, res_flow).move_to((32/9, 0, 0))
        self.play(flow_net.animate.move_to((-32/9, 0, 0), ))
        self.play(Write(res_net))

        # ---Aminate Flow on Flow net---
        flow = animate_flow(self, 4, source, target, 8, 4, flow)

        # ---Aminate Flow on Residual net---
        res_flow, res_parallew = animate_flow_parallel(self, 4, res_source, res_target, 8, 4, res_flow, None)

        # ---Aminate Full Flow on Flow net ---
        flow = animate_flow(self, 4, source, target, 8, 8, flow)

        # ---Aminate Full Flow on Residual net---
        res_flow, res_parallew = animate_flow_parallel(self, 4, res_source, res_target, 8, 8, res_flow, res_parallew)

        self.play(FadeOut(*self.mobjects))

class Push_Relabel(Scene):
    def construct(self):
        vertices, edges = init_flow_net()

        # ---!!!Start Animations!!!---
        # ---Title---
        title = Text("推送-重贴标签算法").scale(2)
        title.set_color(WHITE)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.scale(0.5))
        self.play(title.animate.to_edge(UP))

        subtitle = Text("基本操作").scale(0.8).scale(2)
        self.play(Write(subtitle))
        self.wait()
        self.play(subtitle.animate.scale(0.5))
        self.play(subtitle.animate.next_to(title))

        # ---Stage: overflow at 4, capcity at 8---
        temp_s = standard_vertice(MathTex("v_1")).shift(LEFT*2)
        temp_t = standard_vertice(MathTex("v_2")).shift(RIGHT*2)

        flow = LabeledArrow(label=MathTex("8"))
        update_arrow(flow, temp_s.get_corner(UR), temp_t.get_corner(UL))

        over_flow = LabeledArrow(label=MathTex("4"))
        update_arrow(over_flow, temp_s.get_edge_center(DOWN), temp_s.get_edge_center(DOWN) + DOWN * 2)

        self.play(Write(temp_s), Write(temp_t), Write(flow),)
        self.wait()
        self.play(Write(over_flow))

        animate_flow_parallel(self, 4, )

        # flow_net = VGroup(*vertices.values(), *edges.values())
        # self.play(Write(flow_net))


class test(Scene):
    def construct(self):
        a = LabeledDot(MathTex("v_1", color=BLACK))

        self.add(a)
        a.animate.move_to()



