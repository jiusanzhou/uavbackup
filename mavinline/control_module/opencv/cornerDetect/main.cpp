#include<iostream>
#include<opencv2/highgui/highgui.hpp>
#include<opencv2/video/video.hpp>

#pragma comment(lib,"opencv_calib3d2410.lib" )
#pragma comment(lib,"opencv_core2410.lib" )
#pragma comment(lib,"opencv_features2d2410.lib" )
#pragma comment(lib,"opencv_flann2410.lib" )
#pragma comment(lib,"opencv_highgui2410.lib" )
#pragma comment(lib,"opencv_imgproc2410.lib" )
#pragma comment(lib,"opencv_video2410.lib" )

#ifndef PAUSE
#define PAUSE system("PAUSE")
#endif

#ifndef OCV_KEY_RIGHT
#define OCV_KEY_RIGHT 2555904
#endif

#ifndef OCV_KEY_LEFT
#define OCV_KEY_LEFT 2424832
#endif

#define MAX_WIDTH 20000
#define MAX_HEIGHT 20000

using namespace std;

int main(int argc, char** argv){
	cv::Mat lCurrentFrame;//当前视屏帧
	
	bool lStop = false;
	cv::VideoCapture lCapture;//视频流读取类
	lCapture.open(1);//读取1号相机（-1表示由操作者指定）
	if (!lCapture.isOpened()){
		cout << "Can't open camera 1." << endl;
		PAUSE;
		return -1;
	}
	//lCapture.set(CV_CAP_PROP_FRAME_WIDTH, 1600);
	//lCapture.set(CV_CAP_PROP_FRAME_HEIGHT, 900);//设定分辨率，这里用默认值

	bool startFind = false;
	bool traceCoreSetted = false;
	cv::namedWindow("camera1");//用于显示视屏
	lCapture.set(CV_CAP_PROP_SETTINGS, 0);//windows下以GUI设定相机参数，因为在我的电脑上不能通过设定
										  //CV_CAP_PROP_AUTO_EXPOSURE来关闭自动曝光所以用了这个来设定参数
	if (!lCapture.read(lCurrentFrame)){
		cout << "can't get video stream" << endl;
		PAUSE;
		lCapture.release();
		return false;
	}

	while (!lStop){
		int rKey = cv::waitKey(1);
		if (rKey == 's' || rKey == 'S')lStop = true;
		if (rKey == 't' || rKey == 'T')startFind = true;
		if (!lCapture.read(lCurrentFrame))continue;
		cv::Mat tGray;
		cv::cvtColor(lCurrentFrame, tGray, CV_BGR2GRAY);//转换为灰度图
		cv::Mat cornerStrenth;
		cv::cornerHarris(tGray, cornerStrenth, 3, 3, 0.01);//求harris角点的强度
		cv::Mat harrisCorners;
		double hThres = 0.0003;
		cv::threshold(cornerStrenth, harrisCorners, hThres, 255, cv::THRESH_BINARY);//提取强度足够高的像素点
		int HSSize = MAX_HEIGHT + MAX_WIDTH;
		cv::Point bCP(-1, -1);
		//寻找左上角的角点,保存在bCP中
		for (int i = 0; i < cornerStrenth.rows; i++){
			for (int j = 0; j < cornerStrenth.cols; j++){
				float tPStrenth = cornerStrenth.at<float>(i, j);
				if (tPStrenth >= hThres){
					int tSize = j + i;
					if (tSize < HSSize){
						HSSize = tSize;
						bCP = cv::Point(j, i);
					}
				}
			}
		}
		cv::imshow("harris", harrisCorners);
		cv::circle(lCurrentFrame, bCP, 3, cv::Scalar(0, 255, 255), 2);
		cv::imshow("camera1", lCurrentFrame);
	}
	cv::destroyWindow("camera1");
	lCapture.release();

	return 0;
}