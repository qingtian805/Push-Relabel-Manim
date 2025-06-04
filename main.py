from manim import *
import typing

def relative_direction(a:Mobject, b: Mobject):
    dir = b.get_center() - a.get_center()
    x, y, _ = dir

    vertical = False
    if abs(y) > abs(x):
        vertical = True

    lr = "LEFT" if x < 0 else "RIGHT"
    td = "DOWN" if y < 0 else "UP"

    return td if vertical else lr

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

def init_flow_net() -> tuple[typing.Dict[str, LabeledDot], typing.Dict[tuple[str, str], LabeledArrow]]:
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

def create_overflow(quantity, end_point:LabeledDot, direction):
    overflow = LabeledArrow(label=MathTex(f"{quantity}"))
    update_arrow(overflow, end_point, end_point.get_edge_center(direction)+1.5 * direction)
    
    return overflow

def animate_update_labeleddot(labeled:LabeledDot, new_label:MathTex) -> Transform:
    return Transform(labeled.submobjects[0], new_label.move_to(labeled))

def animate_update_labeledarrow(labeled:LabeledArrow, new_label:MathTex) -> Transform:
    new_arrow = LabeledArrow(label=new_label)
    labeled.label.rendered_label.set(tex_string=new_label.get_tex_string())
    update_arrow(new_arrow, labeled.get_start(), labeled.get_end())
    return Transform(labeled, new_arrow)

def play_animate_flow(scene:Scene, quantity, start: LabeledDot,
                      end: LabeledDot, edge:LabeledArrow,
                      play:Animation = []):
    label = edge.label.rendered_label.get_tex_string().split(sep='/')

    if len(label) > 1:
        capcity = int(label[1])
        used = int(label[0])
    else:
        capcity = int(label[0])
        used = 0

    used += quantity
    if quantity > 10:
        quantity = 10
    
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
        AnimationGroup(*animations, lag_ratio=0.2),
        ),
        *play
    )
    scene.play(FadeOut(*data))
    # new_edge.to_corner()
    scene.add(new_edge)
    scene.remove(edge)

    return new_edge

def play_animate_flow_parallel(scene:Scene, quantity, start: LabeledDot, end: LabeledDot,
                               edge:LabeledArrow, parallel_edge: LabeledArrow =None,
                               play:Animation = []):
    def create_edge(free, direction):
        new_edge = LabeledArrow(label=MathTex(f"{free}"))
        update_arrow(new_edge, start.get_corner(direction[0]), end.get_corner(direction[1]))
        return new_edge
    
    def create_parallel(used, direction):
        new_parallel = LabeledArrow(label=MathTex(f"{used}"))
        update_arrow(new_parallel, end.get_corner(direction[0]), start.get_corner(direction[1]))
        return new_parallel
    # !!Attention: This dict is making sure that we can swap start and end
    #             DIR       edge       para
    #              -      from to   from to
    dir_corner = {"RIGHT": ((UR, UL), (DL, DR)),
                  "LEFT":  ((DL, DR), (UR, UL)),
                  "UP":    ((UL, DL), (DR, UR)),
                  "DOWN":  ((DR, UR), (UL, DL))}
    direction = dir_corner[relative_direction(start, end)]
    
    free = int(edge.label.rendered_label.get_tex_string())
    used = 0
    if parallel_edge is not None:
        used = int(parallel_edge.label.rendered_label.get_tex_string())
    
    free -= quantity
    used += quantity
    if quantity > 10:
        quantity = 10
    data: list[Square] = []
    for i in range(quantity):
        data.append(Square(side_length=0.3, color=BLUE).move_to(start))

    new_edge = None
    new_parallel = None
    # only under case used == capcity edge is not used
    if free > 0:
        new_edge = create_edge(free, direction[0])
    # only under case used == 0 parallel edge is not used
    if used > 0:
        new_parallel = create_parallel(used, direction[1])

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
        AnimationGroup(*data_animations, lag_ratio=0.2),
        ),
        *play
    )
    scene.add(*new_edges)
    scene.remove(edge, parallel_edge)
    scene.remove(*data)

    return new_edge, new_parallel

def play_animate_relabel(scene:Scene, dot:LabeledDot, height, opacity):
    _dot = dot.copy()
    _dot.submobjects[0] = MathTex(f"{height}").move_to(_dot)
    update_dot_fill(_dot, DARK_BLUE, opacity)
    scene.play(Transform(dot, _dot))

def play_animate_push(scene:Scene, start: LabeledDot, end: LabeledDot,
                      edge:LabeledArrow, parallel,
                      oflow_start:LabeledArrow, oflow_end: LabeledArrow = None, oflow_end_direction = DOWN):
    animations = []
    quantity = int(oflow_start.label.rendered_label.get_tex_string())
    capcity = int(edge.label.rendered_label.get_tex_string())
    
    # Update overflow of start point
    if quantity > capcity:
        animations.append(animate_update_labeledarrow(oflow_start, MathTex(f"{quantity-capcity}")))
        quantity = capcity
    else:
        animations.append(FadeOut(oflow_start))
        oflow_start = None
    del capcity
    
    # Update overflow of end point
    if oflow_end is None:
        oflow_end = create_overflow(quantity, end, oflow_end_direction)
        animations.append(Write(oflow_end))
    else:
        origin_quantity = int(oflow_end.label.rendered_label.get_tex_string())
        animations.append(animate_update_labeledarrow(oflow_end, MathTex(f"{origin_quantity + quantity}")))

    scene.play(animations[0])
    edge, parallel = play_animate_flow_parallel(scene, quantity, start, end,\
                                                edge, parallel,\
                                                [animations[1]])
    return edge, parallel, oflow_start, oflow_end

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
        title = Text("残留网络").scale(2)
        title.set_color(WHITE)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.scale(0.5))
        self.play(title.animate.to_edge(UP))

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
        flow = play_animate_flow(self, 4, source, target, flow)

        # ---Aminate Flow on Residual net---
        res_flow, res_parallew = play_animate_flow_parallel(self, 4, res_source, res_target, res_flow, None)

        # ---Aminate Full Flow on Flow net ---
        flow = play_animate_flow(self, 4, source, target, flow)

        # ---Aminate Full Flow on Residual net---
        res_flow, res_parallew = play_animate_flow_parallel(self, 4, res_source, res_target, res_flow, res_parallew)

        self.play(FadeOut(*self.mobjects))

class Push_Relabel(Scene):
    def construct(self):
        # # ---!!!Start Animations!!!---
        # # ---Title---
        # title = Text("推送-重贴标签算法").scale(2)
        # title.set_color(WHITE)
        # self.play(Write(title))
        # self.wait(1)
        # self.play(title.animate.scale(0.5))
        # self.play(title.animate.to_edge(UP))

        # # subtitle = Text("基本操作").scale(0.8).scale(2)
        # self.play(Write(subtitle))
        # self.wait()
        # self.play(subtitle.animate.scale(0.5))
        # self.play(subtitle.animate.next_to(title))

        # # ---Stage: overflow at 8, capcity at 4, target 1h, source 0h---
        # # ---Draw Residual Net---
        # temp_s = standard_vertice(MathTex("v_1")).shift(LEFT*2)
        # temp_t = standard_vertice(MathTex("v_2")).shift(RIGHT*2)
        # update_dot_fill(temp_t, DARK_BLUE, 0.3)

        # flow = LabeledArrow(label=MathTex("4"))
        # update_arrow(flow, temp_s.get_corner(UR), temp_t.get_corner(UL))

        # self.play(Write(temp_s), Write(temp_t), Write(flow),)
        # self.wait()
        # # ---Add Overflow and Height---
        # overflow = create_overflow(8, temp_s, DOWN)

        # temp_s_height = standard_vertice(MathTex("0")).shift(LEFT*2)
        # temp_t_height = standard_vertice(MathTex("1")).shift(RIGHT*2)
        # update_dot_fill(temp_t_height, DARK_BLUE, 0.3)
        
        # self.play(Transform(temp_s, temp_s_height), Transform(temp_t, temp_t_height))
        # self.play(Write(overflow))
        # self.wait()

        # # ---Animating Relabeling---
        # play_animate_relabel(self, temp_s, 2, 0.5)

        # self.wait()

        # # ---Animating Pushing Flow---
        # flow, parallel, overflow, t_overflow = play_animate_push(self, temp_s, temp_t, flow, None, overflow, None)

        # self.play(FadeOut(temp_s, temp_t),
        #           FadeOut(parallel, t_overflow, overflow))
        # self.wait()
        # # ---Cleanning Stage---
        # del temp_s, temp_s_height
        # del temp_t, temp_t_height
        # del flow, overflow, t_overflow, parallel
        
        # ---Init Residual Net and Nessassary Data Structure---
        vertices, edges = init_flow_net()

        parallels = {}
        for i in edges.keys():
            parallels[i] = None

        overflows = {}
        for i in vertices.keys():
            overflows[i] = None

        flow_net = VGroup(*vertices.values(), *edges.values())
        self.play(Write(flow_net))
        self.wait()
        # ---Initalizing---
        animations = []
        for i in vertices.values():
            animations.append(animate_update_labeleddot(i, MathTex("0")))
        animations.append(animate_update_labeleddot(vertices["s"], MathTex("6")))
        self.play(*animations)
        self.wait()

        animations.clear()
        overflows["s"] = create_overflow("16+13", vertices["s"], DOWN)

        self.play(Write(overflows["s"]))
        self.play(animate_update_labeledarrow(overflows["s"], MathTex(f"{16+13}")))
        self.wait()
        
        edges[("s", "v_1")], parallels[("s", "v_1")], overflows["s"], overflows["v_1"] = \
                    play_animate_push(self, vertices["s"], vertices["v_1"], edges[("s", "v_1")], parallels[("s", "v_1")],
                                      overflows["s"], overflows["v_1"], UP)
        
        edges[("s", "v_2")], parallels[("s", "v_2")], overflows["s"], overflows["v_2"] = \
                    play_animate_push(self, vertices["s"], vertices["v_2"], edges[("s", "v_2")], parallels[("s", "v_2")],
                                      overflows["s"], overflows["v_2"], DOWN)
        self.wait()

        # ---Pushing v_1---
        play_animate_relabel(self, vertices["v_1"], 1, 1/12)

        edges[("v_1", "v_3")], parallels[("v_1", "v_3")], overflows["v_1"], overflows["v_3"] = \
                play_animate_push(self, vertices["v_1"], vertices["v_3"], edges[("v_1", "v_3")], parallels[("v_1", "v_3")],
                          overflows["v_1"], overflows["v_3"], UP)
        
        # ---Pushing v_2---
        play_animate_relabel(self, vertices["v_2"], 1, 1/12)

        edges[("v_2", "v_4")], parallels[("v_2", "v_4")], overflows["v_2"], overflows["v_4"] = \
                play_animate_push(self, vertices["v_2"], vertices["v_4"], edges[("v_2", "v_4")], parallels[("v_2", "v_4")],
                          overflows["v_2"], overflows["v_4"], DOWN)
        
        # ---Pushing v_4---
        play_animate_relabel(self, vertices["v_4"], 1, 1/12)

        edges[("v_4", "t")], parallels[("v_4", "t")], overflows["v_4"], overflows["t"] = \
                play_animate_push(self, vertices["v_4"], vertices["t"], edges[("v_4", "t")], parallels[("v_4", "t")],
                          overflows["v_4"], overflows["t"], DOWN)
        edges[("v_4", "v_3")], parallels[("v_4", "v_3")], overflows["v_4"], overflows["v_3"] = \
                play_animate_push(self, vertices["v_4"], vertices["v_3"], edges[("v_4", "v_3")], parallels[("v_4", "v_3")],
                          overflows["v_4"], overflows["v_3"], UP)

        # ---Pushing v_3---
        play_animate_relabel(self, vertices["v_3"], 1, 1/12)

        edges[("v_3", "t")], parallels[("v_3", "t")], overflows["v_3"], overflows["t"] = \
            play_animate_push(self, vertices["v_3"], vertices["t"], edges[("v_3", "t")], parallels[("v_3", "t")],
                  overflows["v_3"], overflows["t"], UP)
        
        self.wait()

        # ---Pushing v_4---
        play_animate_relabel(self, vertices["v_4"], 2, 1/6)

        parallels[("v_2", "v_4")], edges[("v_2", "v_4")], overflows["v_4"], overflows["v_2"] = \
            play_animate_push(self, vertices["v_4"], vertices["v_2"],parallels[("v_2", "v_4")], edges[("v_2", "v_4")],
              overflows["v_4"], overflows["v_2"], DOWN)
        
        # ---Pushing v_1---
        play_animate_relabel(self, vertices["v_1"], 7, 7/12)

        parallels[("s", "v_1")], edges[("s", "v_1")], overflows["v_1"], overflows["s"] = \
            play_animate_push(self, vertices["v_1"], vertices["s"], parallels[("s", "v_1")], edges[("s", "v_1")],
              overflows["v_1"], overflows["s"], DOWN)
        # ---Pushing v_2---
        play_animate_relabel(self, vertices["v_2"], 7, 7/12)

        parallels[("s", "v_2")], edges[("s", "v_2")], overflows["v_2"], overflows["s"] = \
            play_animate_push(self, vertices["v_2"], vertices["s"], parallels[("s", "v_2")], edges[("s", "v_2")],
              overflows["v_2"], overflows["s"], DOWN)
        
        self.wait()



class test(Scene):
    def construct(self):
        pass
        
    def __init__(self):
        direction = UL
        a = standard_vertice(MathTex("1"))
        b = standard_vertice(MathTex("2")).move_to(direction)

        print(direction)
        print(relative_direction(a, b))

if __name__ == "__main__":
    t = test()



