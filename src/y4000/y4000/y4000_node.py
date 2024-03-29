from navigator_interfaces.srv import WaterParameters
import rclpy
from rclpy.node import Node
from rclpy.logging import LoggingSeverity
from y4000.y4000_reader import Sonde
from navigator_interfaces.msg import Y4000msg, ArmStatus
from std_msgs.msg import Header

class Y4000Node(Node):
    def __init__(self):
        super().__init__('y4000_node')
        self.sonde = Sonde('/dev/ttyUSB1',0x01)
        self.attempts = 0
        self.armedstateSubscriber = self.create_subscription(
            ArmStatus,
            'arm_status',
            self.arm_callback,
            10
        )

    def timer_callback(self):
        try:
            self.readings = self.sonde.read_all_sensors()
        except Exception as e:
            self.get_logger().error('Reading from Sonde failed %r' %(e,))
        msg = Y4000msg()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "Y4000"
        for reading in self.readings:
            self.get_logger().info(str(reading))
        msg.odo = self.readings[0]
        msg.turb = self.readings[1]
        msg.ct = self.readings[2]
        msg.ph = self.readings[3]
        msg.temp = self.readings[4]
        msg.orp = self.readings[5]
        msg.chl = self.readings[6]
        try:
            self.publisher.publish(msg)
        except Exception as e:
            self.get_logger().error('Topic publish failed %r' %(e,))
        self.attempts = 0

    def arm_callback(self, message):
        if(message.armed == True):
            self.publisher = self.create_publisher(Y4000msg, 'y4000', 10)
            timer_period = 60
            self.timer = self.create_timer(timer_period, self.timer_callback)
        else:
            if(hasattr(self, "publisher")):
                self.destroy_publisher(self.publisher)
                self.destroy_timer(self.timer)


                



def main(args=None):
    rclpy.init(args=args)
    y4000 = Y4000Node()
    try:
        rclpy.spin(y4000)
    except Exception as e:
        y4000.get_logger().info('Node Spin failed: %r' %(e,))
    rclpy.shutdown()


if __name__ == '__main__':
    main()
