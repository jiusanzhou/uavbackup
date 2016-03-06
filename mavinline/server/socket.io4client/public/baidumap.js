// (function(){

// 百度地图API功能
var currentPoint = localStorage.currentPoint ? JSON.parse(localStorage.currentPoint) : { "lng":117.283,  "lat": 31.867123};
//console.log(currentPoint);
var oCurrentPoint = new BMap.Point(currentPoint.lng, currentPoint.lat);
var convertor = new BMap.Convertor();
var pointArr = [];
var aircraftPlane = new BMap.Marker(oCurrentPoint, {});
pointArr.push(oCurrentPoint);
convertor.translate(pointArr, 1, 5, function(data){
    if(data.status === 0) {
        map.centerAndZoom(oCurrentPoint, 20);
        oCurrentPoint = data.points[0];//设置marker图标为飞机
        var aircraftPlane = new BMap.Marker(oCurrentPoint, {
          // 初始化小飞机Symbol
          icon: new BMap.Symbol(BMap_Symbol_SHAPE_PLANE, {
            scale: 2,
            rotation: 0,    
            fillColor: 'gray',
            fillOpacity: 0.8
          })
        });
        aircraftPlane.setTitle("正在运行机器");
        map.addOverlay(aircraftPlane);
    }
})
//localStorage.currentPoint = new BMap.Point(117.283,31.867123);

var map = new BMap.Map("allmap", {minZoom:4,maxZoom: 20});    // 创建Map实例
map.setCurrentCity("合肥");          // 设置地图显示的城市 此项是必须设置的	

//console.log(currentPoint);
map.addControl(new BMap.MapTypeControl());   //添加地图类型控件
map.enableScrollWheelZoom(true);     //开启鼠标滚轮缩放





function fixSomething(){    
	function _dis(){
	  $('.anchorBL').attr('style', 'display:none');
	}
	function _moveToCenter(){
		map.panTo(oCurrentPoint);
	}
	setTimeout(_dis, 2000);
	setTimeout(_moveToCenter, 2000);
	//console.log("dddd")
}
$(window).load(function() {
	fixSomething();
})

// var wayPoints = [];

// function showPoint(e){
//   //alert(e.point.lng + ", " + e.point.lat);
//   map.openInfoWindow(BMap.InfoWindow(e.point, {
//     width: 200,
//     height: 100,
//     title: 'Add Point'
//   }))
// }
// map.addEventListener("click", function(e){
//   //wayPoints.push([e.point.lng, e.point.lat]);
//   //showPoint(e);
//   console.log('您的位置：'+e.point.lng+','+e.point.lat);
// });
// })()