from manim import *

def update_arrow(arrow:LabeledArrow, start, end):
    tip = arrow.pop_tips()[0]
    arrow.set_points_by_ends(start, end)
    arrow.add_tip(tip)
    arrow.label.move_to(arrow.get_midpoint())

def update_dot_fill(dot:LabeledDot, color, opacity):
    dot.set_fill(color, opacity)
    dot.submobjects[0].set_fill(WHITE, opacity=1)

def animate_flow(scene:Scene, quantity, start: LabeledDot, end: LabeledDot, edge, capcity, used):
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
    edge = new_edge
    scene.add(edge)
    scene.remove(new_edge)

def animate_flow_parallel(scene:Scene, quantity, start: LabeledDot, end: LabeledDot, edge, capcity, used, parallel_edge=None):
    data: list[Square] = []
    for i in range(quantity):
        data.append(Square(side_length=0.3, color=BLUE).move_to(start))
    
    if allow_parallel and capcity - used < capcity and capcity - used > 0:
        new_edge = LabeledArrow(label=MathTex(f"{capcity - used}"))
        parallel_edge = LabeledArrow(label=MathTex(f"{used}"))
        update_arrow(new_edge, start.get_corner(UR), end.get_corner(UL))
        update_arrow(parallel_edge, end.get_corner(DL), start.get_corner(DR))
    elif allow_parallel and capcity - used == capcity:
        new_edge = LabeledArrow(label=MathTex(f"{capcity}"))
        
    animations = [
        mob.animate.move_to(end)
        for mob in data
    ]
    if allow_parallel:
        scene.play(AnimationGroup(
            Transform(edge, new_edge),
            Transform(parallel_edge, )
            AnimationGroup(*animations, lag_ratio=0.3),
            )
        )
    else:
        scene.play(AnimationGroup(
            Transform(edge, new_edge),
            AnimationGroup(*animations, lag_ratio=0.3),
            )
        )
    scene.remove(*data)
    
    
    scene.add(flow)
    scene.remove(new_flow)

def init_flow_net():
    # ---Init Flow_Net---
    # Creating Init Vertices
    vert_label = ["v_1", "v_2", "v_3", "v_4", "s", "t"]
    vertices = {}
    for i in vert_label:
        print(i, type(i))
        vert = LabeledDot(MathTex(i), radius=0.5, stroke_width=2, stroke_color=BLUE, fill_opacity=0)
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
        source = LabeledDot(MathTex("s"), radius=0.5, stroke_width=2, stroke_color=BLUE, fill_opacity=0).shift(LEFT*2)
        target = LabeledDot(MathTex("t"), radius=0.5, stroke_width=2, stroke_color=BLUE, fill_opacity=0).shift(RIGHT*2)

        update_dot_fill(source, DARK_BLUE, 1)

        flow = LabeledArrow(label=MathTex("8"))
        update_arrow(flow, source, target)

        self.play(Write(source), Write(target), Write(flow))

        # ---Make Residual_Net---
        res_source = source.copy()
        res_target = target.copy()
        res_flow   = flow.copy()
        
        flow_net = VGroup(source, target, flow)
        res_net  = VGroup(res_source, res_target, res_flow).move_to((32/9, 0, 0))
        self.play(flow_net.animate.move_to((-32/9, 0, 0), ))
        self.play(Write(res_net))

        # ---Aminate Flow on Flow net---
        data: list[Square] = []
        for i in range(4):
            data.append(Square(side_length=0.3, color=BLUE).move_to(source))

        new_flow = LabeledArrow(label=MathTex("4/8"))
        update_arrow(new_flow, source, target)
        
        self.play(AnimationGroup(
            AnimationGroup(data[0].animate.move_to(target),
                           Transform(flow, new_flow)),
            data[1].animate.move_to(target),
            data[2].animate.move_to(target),
            data[3].animate.move_to(target),
            lag_ratio=0.2
        ))
        self.remove(*data)
        del flow
        flow = new_flow
        self.add(flow)
        self.remove(new_flow)

        # ---Aminate Flow on Residual net---
        for i in data:
            i.move_to(res_source)

        new_flow = LabeledArrow(label=MathTex("4"))
        update_arrow(new_flow, res_source.get_corner(DR), res_target.get_corner(DL))

        parallel_edge = LabeledArrow(label=MathTex("4"))
        update_arrow(parallel_edge, res_target.get_corner(UL), res_source.get_corner(UR))
        
        self.play(AnimationGroup(
            AnimationGroup(data[0].animate.move_to(res_target),
                           Transform(res_flow, new_flow),
                           Write(parallel_edge)),
            data[1].animate.move_to(res_target),
            data[2].animate.move_to(res_target),
            data[3].animate.move_to(res_target),
            lag_ratio=0.2
        ))
        self.remove(*data)
        self.remove(res_flow)
        del res_flow
        res_flow = new_flow

        # ---Aminate Full Flow on Flow net ---
        data: list[Square] = []
        for i in range(4):
            data.append(Square(side_length=0.3, color=BLUE).move_to(source))

        new_flow = LabeledArrow(label=MathTex("4/8"))
        update_arrow(new_flow, source, target)
        
        self.play(AnimationGroup(
            AnimationGroup(data[0].animate.move_to(target),
                           Transform(flow, new_flow)),
            data[1].animate.move_to(target),
            data[2].animate.move_to(target),
            data[3].animate.move_to(target),
            lag_ratio=0.2
        ))
        self.remove(*data)
        del flow
        flow = new_flow
        self.remove(new_flow)
        self.add(flow)

        # ---Aminate Full Flow on Residual net---
        for i in data:
            i.move_to(res_source)

        new_flow = LabeledArrow(label=MathTex("4"))
        update_arrow(new_flow, res_source.get_corner(DR), res_target.get_corner(DL))

        parallel_edge = LabeledArrow(label=MathTex("4"))
        update_arrow(parallel_edge, res_target.get_corner(UL), res_source.get_corner(UR))
        
        self.play(AnimationGroup(
            AnimationGroup(data[0].animate.move_to(res_target),
                           Transform(res_flow, new_flow),
                           Write(parallel_edge)),
            data[1].animate.move_to(res_target),
            data[2].animate.move_to(res_target),
            data[3].animate.move_to(res_target),
            lag_ratio=0.2
        ))
        self.remove(*data)
        del res_flow
        res_flow = new_flow
        self.remove(res_flow)

        

        
        
        

        

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

        flow_net = VGroup(*vertices.values(), *edges.values())
        self.play(Write(flow_net))
        


class test(Scene):
    def construct(self):
        a = LabeledDot(MathTex("v_1", color=BLACK))

        self.add(a)
        a.animate.move_to()



