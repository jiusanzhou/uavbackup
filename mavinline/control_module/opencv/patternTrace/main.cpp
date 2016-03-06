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

using namespace std;

int main(int argc, char** argv){
	cv::Mat lCurrentFrame;
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

	int lTraceColor = 15;//要追踪的色调，默认15
	const double lScale = 8.0;//对图像进行放缩，降低运算量
	int lTraceAreaWidth = 160 / lScale;
	int lTraceAreaHeight = 160 / lScale;
	const cv::Size lSSize(lCurrentFrame.cols / lScale, lCurrentFrame.rows / lScale);//放缩后的图像大小
	cv::Rect lTraceArea = cv::Rect(lSSize.width / 2 - lTraceAreaWidth / 2,
		lSSize.height / 2 - lTraceAreaHeight / 2,
		lTraceAreaWidth, lTraceAreaHeight);//追踪的区域，初始化

	const int lCRadius = max(2, 10);//追踪色调的半径，最小为2
	const int minLength = 160 / lScale;//最小的轮廓长度，用于筛选物体轮廓
	const int channels[1] = { 0 };
	const int histSize[1] = { 180 };
	const float histRanges[2] = { 0.0, 179.0 };
	const float *ranges[1] = { histRanges };//计算色调统计直方图的参数
	const int lVThres = 40;//饱和度的阀值，饱和度越低，越接近白色（RGB三通道值越接近）
	const int lSThres = 20;//亮度的阀值，值越大越亮

	while (!lStop){
		int rKey = cv::waitKey(1);
		if (rKey == 's' || rKey == 'S')lStop = true;
		if (rKey == 't' || rKey == 'T')startTrace = true;
		if (!lCapture.read(lCurrentFrame))continue;
		if (startTrace){
			cv::Mat tRFrame;
			cv::resize(lCurrentFrame, tRFrame, lSSize);//放缩原始图像
			cv::Mat tHSV;
			cv::cvtColor(tRFrame, tHSV, CV_BGR2HSV);//转换为HSV通道值
			vector<cv::Mat> tHSVChannel;
			cv::split(tHSV, tHSVChannel);//将三个通道的值分割出来
			cv::threshold(tHSVChannel[2], tHSVChannel[2], lVThres, 255, CV_THRESH_BINARY);//提取亮度大的区域
			cv::threshold(tHSVChannel[1], tHSVChannel[1], lSThres, 255, CV_THRESH_BINARY);//提取饱和度大的区域
			if (!traceCoreSetted){
				//计算要追踪的色调
				cv::Mat tTraceROI = tHSVChannel[0](lTraceArea);
				cv::MatND tHist;
				cv::calcHist(&tTraceROI, 1, channels, cv::Mat(), tHist, 1, histSize, ranges);//计算色调的直方图，用于统计
				//求色调的峰值（色调较为集中的区域）
				float cPixelCount = 0;
				for (int i = 0; i < histSize[0]; i++){
					float tPixels = 0;
					for (int j = -lCRadius; j <= lCRadius; j++){
						int tSPoint = i + j;
						if (tSPoint>179)tSPoint -= 180;
						else if (tSPoint<0)tSPoint += 180;
						tPixels += tHist.at<float>(tSPoint);
					}
					if (tPixels > cPixelCount){
						lTraceColor = i;
						cPixelCount = tPixels;
					}
				}
				traceCoreSetted = true;
			}
			else{
				//------------------提取与要追踪的色调接近的区域------------------//
				//opencv中色调取值范围为0-179，色调的分布是一个圆，所以0与179对应的色调是很接近的
				//因此需要采取如下处理
				if (lTraceColor + lCRadius > 179){
					int tThres1 = lTraceColor + lCRadius + 1 - 180;
					if (tThres1 > 1) cv::threshold(tHSVChannel[0], tHSVChannel[0], max(0, tThres1), 255, CV_THRESH_TOZERO);
					cv::threshold(tHSVChannel[0], tHSVChannel[0], max(0, lTraceColor - lCRadius -1), 255, CV_THRESH_TOZERO_INV);
					cv::threshold(tHSVChannel[0], tHSVChannel[0], 0, 255, CV_THRESH_BINARY_INV);
				}
				else if (lTraceColor - lCRadius <= 0){
					cv::threshold(tHSVChannel[0], tHSVChannel[0], max(0, lTraceColor + lCRadius + 1), 255, CV_THRESH_TOZERO);
					if (lTraceColor - lCRadius < 0) cv::threshold(tHSVChannel[0], tHSVChannel[0], max(0, lTraceColor + lTraceColor - lCRadius - 1 + 180), 255, CV_THRESH_TOZERO_INV);
					cv::threshold(tHSVChannel[0], tHSVChannel[0], 0, 255, CV_THRESH_BINARY_INV);
				}
				else{
					cv::threshold(tHSVChannel[0], tHSVChannel[0], max(0, lTraceColor - lCRadius - 1), 255, CV_THRESH_TOZERO);
					cv::threshold(tHSVChannel[0], tHSVChannel[0], max(0, lTraceColor + lCRadius + 1), 255, CV_THRESH_TOZERO_INV);
					cv::threshold(tHSVChannel[0], tHSVChannel[0], 0, 255, CV_THRESH_BINARY);
				}
				//----------------------------------------------------------------//
				cv::bitwise_and(tHSVChannel[0], tHSVChannel[1], tHSVChannel[0]);//丢弃饱和度低的区域
				cv::bitwise_and(tHSVChannel[0], tHSVChannel[2], tHSVChannel[0]);//丢弃亮度低的区域
				//进行腐蚀、膨胀、腐蚀，剔除小的区域，让相互靠近的区域结合在一起
				//cv::imshow("traceMap0", tHSVChannel[0]);
				cv::erode(tHSVChannel[0], tHSVChannel[0], cv::Mat(), cv::Point(-1, -1), 1);
				cv::dilate(tHSVChannel[0], tHSVChannel[0], cv::Mat(), cv::Point(-1, -1), 3);
				cv::erode(tHSVChannel[0], tHSVChannel[0], cv::Mat(), cv::Point(-1, -1), 2);
				//------------------------------------------------------------//
				//cv::imshow("traceMap", tHSVChannel[0]);
				vector<vector<cv::Point>> tContours;
				cv::findContours(tHSVChannel[0], tContours, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE);//提取轮廓
				auto cIte = tContours.begin();
				cv::Rect tempTA(-1, -1, 0, 0);
				while (cIte != tContours.end()){
					//筛选出足够长的轮廓，取与上一帧位置最接近的轮廓
					int tLength = cIte->size();
					if (tLength > minLength){
						cv::Rect tBRect = cv::boundingRect(cv::Mat(*cIte));//计算轮廓的包围盒，简化处理
						if (tempTA.x < 0)tempTA = tBRect;
						else{
							int tdx1 = tBRect.x - lTraceArea.x;
							int tdy1 = tBRect.y - lTraceArea.y;
							int tdx2 = tempTA.x - lTraceArea.x;
							int tdy2 = tempTA.y - lTraceArea.y;
							if (tdx1*tdx1 + tdy1*tdy1 < tdx2*tdx2 + tdy2*tdy2){
								tempTA = tBRect;
							}
						}
					}
					cIte++;
				}
				if (tempTA.x > 0){
					lTraceArea = tempTA;
				}
			}
			cv::putText(lCurrentFrame, "Tracing", cv::Point(20, 32), 
				cv::FONT_HERSHEY_SIMPLEX, 1.0, 
				cv::Scalar(0, 255, 0), 2, 8, false);
		}
		cv::rectangle(lCurrentFrame, 
			cv::Rect(lTraceArea.x * lScale, lTraceArea.y * lScale,
			lTraceArea.width * lScale, lTraceArea.height * lScale),
			cv::Scalar(0, 0, 255), 2);
		cv::imshow("camera1", lCurrentFrame);
	}

	cv::destroyWindow("camera1");
	lCapture.release();

	return 0;
}