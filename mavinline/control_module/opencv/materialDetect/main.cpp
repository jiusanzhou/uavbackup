#include<iostream>
#include<cmath>
#include<string>
#include<vector>
#include<opencv2/calib3d/calib3d.hpp>
#include<opencv2/highgui/highgui.hpp>
#include<opencv2/imgproc/imgproc.hpp>
#include<opencv2/video/video.hpp>
#include<opencv2/contrib/contrib.hpp>
#include<Windows.h>

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

bool openFile(string &fileName){
	char lDefaultPath[MAX_PATH];
	GetCurrentDirectory(sizeof(lDefaultPath), lDefaultPath);
	OPENFILENAME ofn;
	char strFile[MAX_PATH];
	memset(&ofn, 0, sizeof(OPENFILENAME));
	memset(strFile, 0, sizeof(strFile));
	ofn.lStructSize = sizeof(OPENFILENAME);
	ofn.lpstrFilter = "image(bmp,jpg,png,...)\0*.*\0";
	ofn.lpstrInitialDir = "D:\\Documents\0";
	ofn.lpstrFile = strFile;
	ofn.nMaxFile = MAX_PATH;
	ofn.Flags = OFN_FILEMUSTEXIST;
	if (GetOpenFileName(&ofn)){
		fileName = strFile;
		SetCurrentDirectory(lDefaultPath);
		return true;
	}
	else{
		SetCurrentDirectory(lDefaultPath);
		return false;
	}
}

int main(int argc, char** argv){
	//-----------------------------------提取材质----------------------------------//
	{
		int materialCount = 0;
		cout << "Please input the count of materials." << endl;
		cin >> materialCount;//输入材质的总数
		const cv::Size sampleSize(64, 64);
		const string sampleTemplateFileName = "template.xml";

		char tBuffer[MAX_PATH];
		cv::FileStorage fs;
		fs.open(sampleTemplateFileName, CV_STORAGE_WRITE);
		fs << "MaterialCount" << materialCount;

		for (int i = 0; i < materialCount; i++){
			sprintf_s(tBuffer, "Material%d", i);
			string tFileName;
			bool selected = false;
			while (!selected){//选择图像文件
				if (openFile(tFileName)){
					cv::Mat tSample;
					//读取图像
					try{
						tSample = cv::imread(tFileName);
					}
					catch (cv::Exception ecp){
						cout << ecp.err << endl;
						continue;
					}
					cv::Rect sampleROI(0, 0, 64, 64);
					cv::namedWindow("selectSample");
					while (!selected){//选取图像的一部分作为材质输入
						int pKey = cv::waitKey(1);
						switch (pKey)
						{
						case 'w':
						case 'W':
							if (sampleROI.y - 15 > 0)sampleROI.y -= 15;
							else sampleROI.y = 0;
							break;
						case 's':
						case 'S':
							if (sampleROI.y + sampleROI.height + 15 < tSample.rows)sampleROI.y += 15;
							else sampleROI.y = tSample.rows - sampleROI.height;
							break;
						case 'a':
						case 'A':
							if (sampleROI.x - 15 > 0)sampleROI.x -= 15;
							else sampleROI.x = 0;
							break;
						case 'd':
						case 'D':
							if (sampleROI.x + sampleROI.width + 15 < tSample.cols)sampleROI.x += 15;
							else sampleROI.x = tSample.cols - sampleROI.width;
							break;
						case 'o':
						case 'O':
							selected = true;
							break;
						default:
							break;
						}
						cv::Mat tempImage;
						tSample.copyTo(tempImage);
						cv::rectangle(tempImage, sampleROI, cv::Scalar(0, 0, 255), 1);
						cv::imshow("selectSample", tempImage);
					}
					cv::destroyWindow("selectSample");
					cv::Mat tHSV;
					cv::cvtColor(tSample(sampleROI), tHSV, CV_BGR2HSV);//将材质转换到HSV空间，并取H（色调）研究
					/*vector<cv::Mat> splitedHSV;
					cv::split(tHSV, splitedHSV);*/
					cv::MatND tHist;
					static const int channels[1] = { 0 };
					static const int histSize[1] = { 180 };//将统计区间分为180段
					static const float histRanges[2] = { 0.0, 180.0 };//取这一部分进行统计
					static const float *ranges[1] = { histRanges };
					cv::calcHist(&tHSV, 1, channels, cv::Mat(), tHist, 1, histSize, ranges);//计算材质的色调分布
					fs << tBuffer << tHist;//保存色调分布
					cout << "material " << i << " saved" << endl;
				}
			}
		}

		fs.release();
		PAUSE;
	}
	//-----------------------------------判断材质----------------------------------//
	{
		vector<cv::MatND> sTemp;
		char tBuffer[MAX_PATH];
		int materialCount;
		cv::FileStorage fl;
		fl.open("template.xml", CV_STORAGE_READ);
		fl["MaterialCount"] >> materialCount;
		cout << "There are " << materialCount << " materials." << endl;
		for (int i = 0; i < materialCount; i++){
			sprintf_s(tBuffer, "Material%d", i);
			cv::MatND tHist;
			fl[tBuffer] >> tHist;
			sTemp.push_back(tHist);
			cout << "material " << i << " loaded" << endl;
		}
		fl.release();

		bool allChecked = false;
		string tFileName;
		while (!allChecked){
			if (openFile(tFileName)){
				cv::Mat tSample;
				try{
					tSample = cv::imread(tFileName);
				}
				catch (cv::Exception ecp){
					cout << ecp.err << endl;
					continue;
				}
				cv::Rect sampleROI(0, 0, 64, 64);
				cv::namedWindow("selectSample");
				bool selected = false;
				while (!selected){
					int pKey = cv::waitKey(1);
					switch (pKey)
					{
					case 'w':
					case 'W':
						if (sampleROI.y - 15 > 0)sampleROI.y -= 15;
						else sampleROI.y = 0;
						break;
					case 's':
					case 'S':
						if (sampleROI.y + sampleROI.height + 15 < tSample.rows)sampleROI.y += 15;
						else sampleROI.y = tSample.rows - sampleROI.height;
						break;
					case 'a':
					case 'A':
						if (sampleROI.x - 15 > 0)sampleROI.x -= 15;
						else sampleROI.x = 0;
						break;
					case 'd':
					case 'D':
						if (sampleROI.x + sampleROI.width + 15 < tSample.cols)sampleROI.x += 15;
						else sampleROI.x = tSample.cols - sampleROI.width;
						break;
					case 'o':
					case 'O':
						selected = true;
						break;
					default:
						break;
					}
					cv::Mat tempImage;
					tSample.copyTo(tempImage);
					cv::rectangle(tempImage, sampleROI, cv::Scalar(0, 0, 255), 1);
					cv::imshow("selectSample", tempImage);
				}
				cv::destroyWindow("selectSample");
				cv::Mat tHSV;
				cv::cvtColor(tSample(sampleROI), tHSV, CV_BGR2HSV);
				cv::MatND tHist;
				static const int channels[1] = { 0 };
				static const int histSize[1] = { 180 };//将统计区间分为180段
				static const float histRanges[2] = { 0.0, 180.0 };//取这一部分进行统计
				static const float *ranges[1] = { histRanges };
				cv::calcHist(&tHSV, 1, channels, cv::Mat(), tHist, 1, histSize, ranges);
				int matrl = -1;
				double matrlRef = 0.0;
				for (int i = 0; i < materialCount; i++){
					double tRef = cv::compareHist(tHist, sTemp[i], CV_COMP_INTERSECT);//计算当前区域与材质库的相似度，值越大越相似，
																					  //可以设置一个阀值，相似度低于这个值则判断不
																					  //在材质库中
					cout << "material" << i << ":" << tRef << " ";
					if (tRef>matrlRef){
						matrl = i;
						matrlRef = tRef;
					}
				}
				cout << endl << "material" << matrl << endl;//输出
			}
			else allChecked = true;
		}
	}

	return 0;
}