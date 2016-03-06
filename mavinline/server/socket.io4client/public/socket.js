$(function() {
  var _admin =  localStorage.admin_name;
  if (_admin) {
    $('.usernameInput').val(_admin);
  };
  var FADE_TIME = 150; // ms
  var TYPING_TIMER_LENGTH = 400; // ms
  var COLORS = [
    '#e21400', '#91580f', '#f8a700', '#f78b00',
    '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
    '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
  ];

  // Initialize varibles
  var $window = $(window);
  var $usernameInput = $('.usernameInput'); // Input for username
  var $messages = $('.messages'); // Messages area
  var $inputMessage = $('.inputMessage'); // Input message input box

  var $loginPage = $('.login.page'); // The login page
  var $chatPage = $('.chat.page'); // The chatroom page

  // Prompt for setting a username
  var username;
  var connected = false;
  var typing = false;
  var lastTypingTime;
  var $currentInput = $usernameInput.focus();

  var socket = io();

  var last_command_time = 0;
  var lastRotation = 0;

  function addParticipantsMessage (data) {
    var message = '';
    if (data.numUsers === 1) {
      message += "1 位管理员登陆";
    } else {
      message += "共 " + data.numUsers + " 位登录";
    }
    log(message);
  }

  // Sets the client's username
  function setUsername () {
    username = cleanInput($usernameInput.val().trim());

    // If the username is valid
    if (username) {
      $loginPage.fadeOut();
      $chatPage.show();
      $loginPage.off('click');
      $currentInput = $inputMessage.focus();
      localStorage.admin_name = username;
      // Tell the server your username
      socket.emit('add user', username);
    }
  }

  // Sends a command
  function sendCommand () {
    var message = $inputMessage.val();
    // Prevent markup from being injected into the message
    message = cleanInput(message);
    // if there is a non-empty message and a socket connection
    if (message && connected) {
      $inputMessage.val('');
      // tell server to execute 'new message' and send along one parameter
      var t = Date.now();
      if (t - last_command_time > 2000) {
        addLogMessage({
          username: username,
          message: message
        });
        socket.emit('new command', message);
        console.log(message);
        last_command_time = t;
      }else{
        addLogMessage({
          username: 'System',
          message: '命令请求太频繁,我会爆掉啦...'
        });
      };
    }
  }

  // Log a message
  function log (message, options) {
    var $el = $('<li>').addClass('log').text(message);
    addMessageElement($el, options);
  }

  // Adds the visual chat message to the message list
  function addLogMessage (data, options) {
    // Don't fade the message in if there is an 'X was typing'
    var $typingMessages = getTypingMessages(data);
    options = options || {};
    if ($typingMessages.length !== 0) {
      options.fade = false;
      $typingMessages.remove();
    }

    var $usernameDiv = $('<span class="username"/>')
      .text(data.username)
      .css('color', getUsernameColor(data.username));
    var $messageBodyDiv = $('<span class="messageBody">')
      .text(data.message);

    var typingClass = data.typing ? 'typing' : '';
    var $messageDiv = $('<li class="message"/>')
      .data('username', data.username)
      .addClass(typingClass)
      .append($usernameDiv, $messageBodyDiv);

    addMessageElement($messageDiv, options);
  }

  // Adds the visual chat typing message
  function addChatTyping (data) {
    data.typing = true;
    data.message = 'is typing';
    addLogMessage(data);
  }

  // Removes the visual chat typing message
  function removeChatTyping (data) {
    getTypingMessages(data).fadeOut(function () {
      $(this).remove();
    });
  }

  // Adds a message element to the messages and scrolls to the bottom
  // el - The element to add as a message
  // options.fade - If the element should fade-in (default = true)
  // options.prepend - If the element should prepend
  //   all other messages (default = false)
  function addMessageElement (el, options) {
    var $el = $(el);

    // Setup default options
    if (!options) {
      options = {};
    }
    if (typeof options.fade === 'undefined') {
      options.fade = true;
    }
    if (typeof options.prepend === 'undefined') {
      options.prepend = false;
    }

    // Apply options
    if (options.fade) {
      $el.hide().fadeIn(FADE_TIME);
    }
    if (options.prepend) {
      $messages.prepend($el);
    } else {
      $messages.append($el);
    }
    $messages[0].scrollTop = $messages[0].scrollHeight;
  }

  // Prevents input from having injected markup
  function cleanInput (input) {
    return $('<div/>').text(input).text();
  }

  // Updates the typing event
  function updateTyping () {
    if (connected) {
      if (!typing) {
        typing = true;
        socket.emit('typing');
      }
      lastTypingTime = (new Date()).getTime();

      setTimeout(function () {
        var typingTimer = (new Date()).getTime();
        var timeDiff = typingTimer - lastTypingTime;
        if (timeDiff >= TYPING_TIMER_LENGTH && typing) {
          socket.emit('stop typing');
          typing = false;
        }
      }, TYPING_TIMER_LENGTH);
    }
  }

  // Gets the 'X is typing' messages of a user
  function getTypingMessages (data) {
    return $('.typing.message').filter(function (i) {
      return $(this).data('username') === data.username;
    });
  }

  // Gets the color of a username through our hash function
  function getUsernameColor (username) {
    // Compute hash code
    var hash = 7;
    for (var i = 0; i < username.length; i++) {
       hash = username.charCodeAt(i) + (hash << 5) - hash;
    }
    // Calculate color
    var index = Math.abs(hash % COLORS.length);
    return COLORS[index];
  }

  // Update aircraft status
  function updateAircraftStatus (data) {
    //console.log(data.message);
    var _s = JSON.parse(data.message.replace(/\'/g, '"'));
    setStatusDisplay(_s);
    var _g = _s.g;
    updateMap(_g);
  }

  // Set status display
  function setStatusDisplay(s){
    var _s = s.s;
    var _c = s.c;
    var _g = s.g;
    var _i = s.i;
    var _d = s.d;
    //console.log(_s);
    $('#voltage').val(_s.v);
    $('#current').val(_s.c);
    for (var i = 0; i < 8; i++) {
      $('#rcchannel' + i).val(_c[i]);
    };    
    $('#gpsLon').val(_g.o);
    $('#gpsLat').val(_g.a);
    $('#gpsHead').val(_g.d * 0.01);
    $('#gpsRelativeAlt').val(_g.h * 0.001);
    $('#rawImuZacc').val(_i.za);
    $('#rawImuXacc').val(_i.xa);
    $('#rawImuYacc').val(_i.ya);

    $('#distance-Left').val(_d.l);
    $('#distance-Right').val(_d.rt);
    $('#distance-Front').val(_d.f);
    $('#distance-Rear').val(_d.rr);
  }


  // Set plane point on map
  var timerId = 0;
  function updateMap(point){
    if ( timerId != 0 ){
      clearTimeout(timerId);
    }
    var _p = new BMap.Point(point.o * 0.0000001, point.a * 0.0000001);
    if (point.o != 0) {
      var convertor = new BMap.Convertor();
      var pointArr = [];
      pointArr.push(_p);
      convertor.translate(pointArr, 1, 5, function(data){
        if(data.status === 0) {
          aircraftPlane.setPosition(data.points[0]);
        }
      })
    };
    // console.log(point.h);
    aircraftPlane.setColor('red');
    _h = point.d;
    if (_h != lastRotation) {
      aircraftPlane.setRotation(_h * 0.01);
      lastRotation = _h;
    };
    timerId = setTimeout(offlineStatus, 2000);
  }

  // Set plane off line

  function offlineStatus(){
    aircraftPlane.setColor('gray');
  }

  // Keyboard events

  $window.keydown(function (event) {
    // Auto-focus the current input when a key is typed
    if (!(event.ctrlKey || event.metaKey || event.altKey)) {
      $currentInput.focus();
    }
    // When the client hits ENTER on their keyboard
    if (event.which === 13) {
      if (username) {
        sendCommand();
        socket.emit('stop typing');
        typing = false;
      } else {
        setUsername();
      }
    }
  });

  $inputMessage.on('input', function() {
    updateTyping();
  });

  // Click events

  // Focus input when clicking anywhere on login page
  $loginPage.click(function () {
    $currentInput.focus();
  });

  // Focus input when clicking on the message input's border
  $inputMessage.click(function () {
    $inputMessage.focus();
  });

  // Socket events

  // Whenever the server emits 'login', log the login message
  socket.on('login', function (data) {
    connected = true;
    // Display the welcome message
    var message = "– 欢迎使用清洁机web控制台 – ";
    log(message, {
      prepend: true
    });
    addParticipantsMessage(data);
  });

  // Whenever the server emits 'log message', update the chat body
  socket.on('log message', function (data) {
    addLogMessage(data);
  });

  // Whenever the server emits 'user joined', log it in the chat body
  socket.on('user joined', function (data) {
    log(data.username + ' 登录');
    addParticipantsMessage(data);
  });

  // Whenever the server emits 'user left', log it in the chat body
  socket.on('user left', function (data) {
    log(data.username + ' 退出');
    addParticipantsMessage(data);
    removeChatTyping(data);
  });

  // Whenever the server emits 'typing', show the typing message
  socket.on('typing', function (data) {
    addChatTyping(data);
  });

  // Whenever the server emits 'stop typing', kill the typing message
  socket.on('stop typing', function (data) {
    removeChatTyping(data);
  });

  // Whenever the server emits 'update status', update status.
  socket.on('update status', function (data) {
    updateAircraftStatus(data);
  });

  socket.on('new command', function(data){
    console.log(data)
  });

  // buttons evets
  $('#arm').click(function(){
    socket.emit('new command', 'hh arm')
  });
  $('#disarm').click(function(){
    socket.emit('new command', 'hh disarm')
  });
  $('#TRL').click(function(){
    socket.emit('new command', 'hh land')
  });
  $('#takeoff').click(function(){
    socket.emit('new command', 'hh takeoff')
  });
  $('#test').click(function(){
    socket.emit('new command', 'test')
  });


  // live camera
  cameraIsOpened = 0;
  $('#open_camera_btn').click(function(){
    console.log("dsd");
      if (!cameraIsOpened) {
          $('#open_camera_btn').text('关闭摄像头');
          var live_camera_name = $('#live-camera-name').val();
          var live_camera_width = $('#live-camera-width').val();
          var live_camera_height = $('#live-camera-height').val(); 

          socket.emit('stream camera', {
              name: live_camera_name,
              width: live_camera_width,
              height: live_camera_height
          });

          var client = new WebSocket( 'ws://127.0.0.1:3001/'+live_camera_name+'/'+live_camera_width+'/'+live_camera_height+'/' );
          var canvas = document.getElementById('videoCanvas');    
          var player = new jsmpeg(client, {canvas:canvas});
          $('#live-camera').css({width: live_camera_width, height: live_camera_height, display: 'block'})
          cameraIsOpened = 1;
      } else{
          $('#open_camera_btn').text('打开摄像头');
          $('#live-camera').css({display: 'none'});
          socket.emit('stop camera', {
              name: live_camera_name,
              width: live_camera_width,
              height: live_camera_height
          });
          cameraIsOpened = 0;
      };
  })

});