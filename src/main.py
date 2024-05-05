import turtle
import py_trees
import functools

import constants
import turtle_food
import turtle_bot
import utils


def main():
    bb = py_trees.blackboard.Client(name=constants.BLACKBOARD_NAME)

    bot = turtle_bot.Bot(turtle.Turtle())
    feed = turtle_food.Feed(turtle.Turtle(), bb)

    # Turtle behavior
    root = py_trees.composites.Sequence("Root Sequence",True, [
        py_trees.composites.Selector("喋る Sequence",True, [
            py_trees.composites.Sequence("０秒間何も食べていない場合", False,[
                turtle_bot.TurtleCheckLastTimeWithoutFood("０秒チェック", bot, 0, 10000),
                turtle_bot.TurtleSpeak("喋る", bot, "幸せ！٩(ˊᗜˋ*)و"),
            ]),
            py_trees.composites.Sequence("１０秒間何も食べていない場合", False,[
                turtle_bot.TurtleCheckLastTimeWithoutFood("１０秒チェック", bot, 10000, 20000),
                turtle_bot.TurtleSpeak("喋る", bot, "お腹すいた！ご飯くれる？(´ﾟωﾟ｀)"),
            ]),
            py_trees.composites.Sequence("２０秒間何も食べていない場合", False,[
                turtle_bot.TurtleCheckLastTimeWithoutFood("２０秒チェック", bot, 20000, 999999),
                turtle_bot.TurtleSpeak("喋る", bot, "お腹すいて死にそうだよおおお( ´༎ຶㅂ༎ຶ`)"),
            ]),
        ]),
        py_trees.composites.Sequence("動く Sequence",True, [
            turtle_bot.TurtleFindClosestFood("餌があるか確認", bot),
            turtle_bot.TurtleMoveToClosestFood("餌の方向に進む", bot),
            turtle_bot.TurtleCheckIfFoodIsWithinEatingRange("餌が食べれる範囲にある？", bot),
            turtle_bot.TurtleEatFood("餌を食べる", bot),
            turtle_bot.TurtleResetTimeWithoutFood("TimeWithoutFoodリセット", bot),
            py_trees.decorators.Condition(
                "食べる Condition", 
                py_trees.composites.Sequence("3秒間食べる Sequence", True, [
                    turtle_bot.TurtleSpeak("喋る", bot, "うまい！( ◍′༥‵*◍)"),
                    utils.Timer("もぐもぐ", 3000),
                ]), 
                py_trees.common.Status.SUCCESS
            )
        ]),
    ])

    screen = turtle.Screen()
    screen.setup(width=600, height=600)
    screen.title("Behavior tree demonstration - robot")
    screen.onclick(feed.place)

    def post_tick_handler(snapshot_visitor, behaviour_tree):
        print(
            py_trees.display.unicode_tree(
                behaviour_tree.root,
                visited=snapshot_visitor.visited,
                previously_visited=snapshot_visitor.visited
            )
        )
        print(bot.get_time_without_food_ms())

    behaviour_tree = py_trees.trees.BehaviourTree(root)
    snapshot_visitor = py_trees.visitors.SnapshotVisitor()
    behaviour_tree.add_post_tick_handler(
        functools.partial(post_tick_handler,
                        snapshot_visitor))
    behaviour_tree.visitors.append(snapshot_visitor)

    # Loop behaviors during program lifetime
    def tick():
        if (root.status == py_trees.common.Status.SUCCESS):
            behaviour_tree.setup()
        behaviour_tree.tick()
        turtle.ontimer(tick, constants.TICK_MS)

    turtle.ontimer(tick, constants.TICK_MS)

    turtle.done()


if __name__ == "__main__":
    main()
