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

#define UNKNOWN_FLOW_THRESH 1e3

using namespace std;

int main(int argc, char** argv){
	cv::Mat lCurrentFrame;
	cv::Mat traceCore;
	bool lStop = false;
	cv::VideoCapture lCapture;
	lCapture.open(1);
	if (!lCapture.isOpened()){
		cout << "Can't open camera 1." << endl;
		PAUSE;
		return -1;
	}

	bool startTrace = false;
	bool traceCoreSetted = false;
	cv::namedWindow("camera1");

	if (!lCapture.read(lCurrentFrame)){
		cout << "can't get video stream" << endl;
		PAUSE;
		lCapture.release();
		return false;
	}

	lCapture.set(CV_CAP_PROP_SETTINGS, 0);

	int trw = 320;
	int trh = 320;
	cv::Rect ROI = cv::Rect(lCurrentFrame.cols / 2 - trw / 2, lCurrentFrame.rows / 2 - trh / 2, trw, trh);//设定进行光流计算的区域

	while (!lStop){
		int rKey = cv::waitKey(1);
		if (rKey == 's' || rKey == 'S')lStop = true;
		if (rKey == 't' || rKey == 'T')startTrace = true;//开始计算光流
		if (!lCapture.read(lCurrentFrame))continue;
		cv::Mat tGray;
		cv::cvtColor(lCurrentFrame, tGray, CV_BGR2GRAY);//转换为灰度图
		cv::circle(lCurrentFrame, 
			cv::Point(lCurrentFrame.cols / 2, lCurrentFrame.rows / 2), 5, 
			cv::Scalar(0, 0, 255), 1);//标记图像中心
		cv::rectangle(lCurrentFrame, ROI, cv::Scalar(0, 0, 255), 2);
		if (startTrace){
			if (!traceCoreSetted){
				traceCore = tGray(ROI);
				traceCoreSetted = true;
			}
			else{
				cv::Mat tFlow;
				cv::Mat tTestArea = tGray(ROI);
				cv::calcOpticalFlowFarneback(traceCore, tTestArea, tFlow, 0.5, 3, 15, 3, 5, 1.2, 0);//计算光流
				double transX = 0.0;
				double transY = 0.0;
				int vCount = 0;
				for (int i = 0; i < tFlow.rows; i++){
					for (int j = 0; j < tFlow.cols; j++){
						cv::Vec2f flow_at_point = tFlow.at<cv::Vec2f>(i, j);
						float fx = flow_at_point[0];
						float fy = flow_at_point[1];
						if (fabs(fx)>UNKNOWN_FLOW_THRESH || fabs(fy) > UNKNOWN_FLOW_THRESH)continue;//去除过大的值
						vCount++;
						transX += fx;
						transY += fy;
					}
				}//计算平均位移
				transY *= 4.0;
				transX *= 4.0;//放大平均位移
				cv::circle(lCurrentFrame, 
					cv::Point2d(lCurrentFrame.cols / 2 + transX / vCount, lCurrentFrame.rows / 2 + transY / vCount), 
					3, cv::Scalar(255, 0, 0), 2);//在图像中显示出来
				traceCore = tGray(ROI);
			}
		}
		cv::imshow("camera1", lCurrentFrame);
	}

	cv::destroyWindow("camera1");
	lCapture.release();

	return 0;
}