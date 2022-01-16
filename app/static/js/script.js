//id属性がtopBtnの要素をクリックすると
$("#scroll_top").click(function(){
    //画面の上から0pxの所まで500ミリ秒（0.5秒）かけてアニメーションしながらスクロールする
    $("html, body").animate({scrollTop: 0}, 500);
});

// 推移ボタンをクリックでモーダルウインドウを表示
$(".login-modal-button").click(function(){
  $("#login-modal").fadeIn(0);
});
$(document).on("click touchend", function(event) {
  // モーダル以外の部分をクリックしたときにモーダルを閉じる
  if (!$(event.target).closest(".login-modal-button,.login-username,.login-password").length) {
    $("#login-modal").fadeOut(0);
  }
});

// 検索ボタンをクリックでモーダルウインドウを表示
$(".search-button").click(function(){
    $("#search-modal").fadeIn(0);
});
$(document).on("click touchend", function(event) {
    // モーダル以外の部分をクリックしたときにモーダルを閉じる
    if (!$(event.target).closest(".search-button,.search-text").length) {
      $("#search-modal").fadeOut(0);
    }
});

// 推移ボタンをクリックでモーダルウインドウを表示
$(".trans-button").click(function(){
    $("#trans-modal").fadeIn(0);
});
$(document).on("click touchend", function(event) {
    // モーダル以外の部分をクリックしたときにモーダルを閉じる
    if (!$(event.target).closest(".trans-button,.search-text").length) {
      $("#trans-modal").fadeOut(0);
    }
});

//ツールバーを上スクロールで表示、下スクロールで非表示にする
$(function(){

    var pos = 0;
    var toolbar = $(".toolbar");
  
    $(window).on("scroll", function(){
      if($(this).scrollTop() < pos ){
        //上スクロール時表示
        toolbar.slideDown();
      }else{
        //下スクロール時非表示
        toolbar.slideUp();
      }
      pos = $(this).scrollTop();
    });
  
  });