var b = require('bonescript');
b.pinMode('P9_12', b.INPUT);
b.pinMode('P9_15', b.OUTPUT);

var l, h, i=0;
var j=0;

setInterval(measure,10000);

function measure(){
  b.digitalWrite('P9_15', b.HIGH);
  setTimeout(getdata, 1);
}

function getdata(){
  b.digitalWrite('P9_15', b.LOW);
  while(j==0){
    //console.log(111);
    b.digitalRead('P9_12', gettime)
  }
}

function gettime(x){
  console.log(x.value);
  if(x.value){
    h = Date.getTime();
    i = 1;
  }else{
    if(i==1){
      j = 1;
      console.log((h-l)*340/2);
    }
    l = Date.getTime();
  }
}
