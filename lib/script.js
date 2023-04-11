  
  (function(funcName, baseObj) {
    document.getElementById('auto').addEventListener("click", function(event) {
            var x = event.clientX;
            var y = event.clientY;
            console.log(x,y);
        $(auto).append($('<div class="damage_dot">a</div>').css({
                            left: x + 'px',
                            top: y + 'px',
                            }));  // Add your code here
      });
})("docReady", window);
   

