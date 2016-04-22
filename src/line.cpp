#include <ros/ros.h>
#include <std_msgs/Float64.h>
#include <image_transport/image_transport.h>
#include <cv_bridge/cv_bridge.h>
#include <sensor_msgs/image_encodings.h>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

class Line_trace
{
  ros::NodeHandle nh_;
  image_transport::ImageTransport it_;
  image_transport::Subscriber image_sub_;
  image_transport::Publisher image_pub_;
  ros::Publisher pub;
  ros::Publisher pub2;
  
public:
  Line_trace()
    : it_(nh_)
  {
    image_sub_ = it_.subscribe("/cv_camera/image_raw", 1, &Line_trace::imageCb, this);
    image_pub_ = it_.advertise("/image_topic", 1);
    pub = nh_.advertise<std_msgs::Float64>("/e", 1);
    pub2 = nh_.advertise<std_msgs::Float64>("/center", 1);
 }

  ~Line_trace()
  {
    cv::destroyAllWindows();
}

  void imageCb(const sensor_msgs::ImageConstPtr& msg)
  {
    cv_bridge::CvImagePtr cv_ptr, cv_ptr2, cv_ptr3;
    try
    {
        cv_ptr    = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
    }
    catch (cv_bridge::Exception& e)
    {
        ROS_ERROR("cv_bridge exception: %s", e.what());
        return;
    }
    std_msgs::Float64 foo, bar;
    cv::Mat hsv_image, color_mask, gray_image, cv_image2, cv_image3;
    //change rgb ro hsv
    cv::cvtColor(cv_ptr->image, hsv_image, CV_BGR2HSV);
    cv::inRange(hsv_image, cv::Scalar(0, 0, 0) , cv::Scalar(180, 180, 90), color_mask);
    //line and point
    int width, height, line_1, line_2;
    width = color_mask.cols;
    height = color_mask.rows;
    line_1 = height / 2;
    line_2 = height / 2 - 30;
    //line
    cv::line(cv_ptr->image, cv::Point(100,line_1), cv::Point(width-100, line_1), CV_RGB(255, 0, 0), 2);
    cv::line(cv_ptr->image, cv::Point(100,line_2), cv::Point(width-100, line_2), CV_RGB(0, 0, 255), 2);
    int count[] = {0,0}, sensor_data[] = {0,0};
    
    for (int i = 100; i < width-100; i++) {
        if (int(color_mask.at<uchar>(line_1, i)) == 255){
            count[0]++;
            sensor_data[0] += i;
        }
        if (int(color_mask.at<uchar>(line_2, i)) == 255){
            count[1]++;
            sensor_data[1] += i;
        }
    }
    int point_1, point_2, e, center;
    if (count[0] != 0 && count[1] != 0){
        point_1 = sensor_data[0] / count[0];
        point_2 = sensor_data[1] / count[1];
        cv::circle(cv_ptr->image, cv::Point(point_1, line_1), 5, CV_RGB(0,255,0));
        cv::circle(cv_ptr->image, cv::Point(point_2, line_2), 5, CV_RGB(0,255,0));
        cv::line(cv_ptr->image, cv::Point(point_1,line_1), cv::Point(point_2, line_2), CV_RGB(0, 255, 0), 3);
        e = point_2 - point_1;
        center = (point_2 + point_1) / 2;
    }
    else {
        std::cout << "No line " << std::endl;
        e = 0;
        center = 0;
    } 
    foo.data = e;
    bar.data = center;

    // resize
    //cv::Mat cv_half_image, cv_half_image2;
    //cv::resize(cv_ptr->image, cv_half_image,cv::Size(),0.5,0.5);
    //cv::resize(color_mask, cv_half_image2,cv::Size(),0.5,0.5);

    // window
    //cv::imshow("Original Image", cv_half_image);
    //cv::imshow("Result Image", cv_half_image2);
    //cv::waitKey(3);
    
    image_pub_.publish(cv_ptr->toImageMsg());
    pub.publish(foo);
    pub2.publish(bar);
  }
};

int main(int argc, char** argv)
{
  ros::init(argc, argv, "image_convert");
  Line_trace ic;
  ros::spin();
  return 0;
}
