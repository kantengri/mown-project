import rospy
import actionlib
from tf.transformations import quaternion_from_euler

from abstractnode import AbstractNode

from geometry_msgs.msg import PoseStamped, Pose, Quaternion
from move_base_mod.msg import TrajectoryControllerAction, TrajectoryControllerGoal

from enginx_msgs.msg import LocalTrajectoryStamped


class BridgeToMoveBase(AbstractNode):
    
    def initialization(self):
        self._publish_rate = rospy.get_param('~publish_rate', 10)
        self.client = actionlib.SimpleActionClient('move_base_mod', TrajectoryControllerAction)
        # rospy.Subscriber("goal", PoseStamped, self.goal_cb)
        self.client.wait_for_server()

        rospy.Subscriber('/local_trajectory_plan', LocalTrajectoryStamped, self.__route_callback)

    def local_trajectory_callback(self, message: LocalTrajectoryStamped):
        poses = list()
        for pose in message.route:
            poses.append(self.__Posed2DtoPoseStamped(pose))

        self.send_msg(poses)

    def goal_cb(self, msg : PoseStamped):
        self.send_msg(msg)

    def __Posed2DtoPoseStamped(self, pose2d):
        pose = Pose()
        pose.position.x = pose2d.x
        pose.position.y = pose2d.y
        pose_or = quaternion_from_euler(0, 0, pose2d.theta)
        pose.orientation.x = pose_or[0]
        pose.orientation.y = pose_or[1]
        pose.orientation.z = pose_or[2]
        pose.orientation.w = pose_or[3]

        posestamped = PoseStamped()
        posestamped.pose = pose
        posestamped.header.stamp = rospy.get_rostime()

        return posestamped


    def send_msg(self, msg : list):
        goal = TrajectoryControllerGoal()
        goal.poses = msg
        self.client.send_goal(goal)
        self.client.wait_for_result()
        return self.client.get_result()

    # def run(self):
    #     self.client.wait_for_server()
    #     rate = rospy.Rate(self._publish_rate)
    #     rospy.spin()
        # while not rospy.is_shutdown():
        #     rate.sleep()

def main():
    rospy.init_node('simple_planner_node')

    node = BridgeToMoveBase()
    node.run()


if __name__ == '__main__':
    main()