document.addEventListener('DOMContentLoaded', function() {
    function onMessage(event) {
        var data = JSON.parse(event.data);
        switch (data.event) {
            case "next": Reveal.next(); break;
            case "prev": Reveal.prev(); break;
            default:
                console.log("Unhandled event: " + data.event);
        }
    }

    function isFunction(functionToCheck) {
      return functionToCheck && {}.toString.call(functionToCheck) === '[object Function]';
    }

    function debounce(func, wait) {
        var timeout;
        var waitFunc;

        return function() {
            if (isFunction(wait)) {
                waitFunc = wait;
            }
            else {
                waitFunc = function() { return wait };
            }

            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                func.apply(context, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, waitFunc());
        };
    }

    // reconnectFrequencySeconds doubles every retry
    var reconnectFrequencySeconds = 1;
    var evtSource;

    var reconnectFunc = debounce(function() {
        setupEventSource();
        // Double every attempt to avoid overwhelming server
        reconnectFrequencySeconds *= 2;
        // Max out at ~1 minute as a compromise between user experience and server load
        if (reconnectFrequencySeconds >= 64) {
            reconnectFrequencySeconds = 64;
        }
    }, function() { return reconnectFrequencySeconds * 1000 });

    function setupEventSource() {
        evtSource = new EventSource("/sse");
        evtSource.onmessage = function(e) {
          onMessage(e);
        };
        evtSource.onopen = function(e) {
          // Reset reconnect frequency upon successful connection
          reconnectFrequencySeconds = 1;
        };
        evtSource.onerror = function(e) {
          evtSource.close();
          reconnectFunc();
        };
    }
    setupEventSource();

    Reveal.on( 'slidechanged', event => {
        navigator.sendBeacon("/slide", new URLSearchParams({html: event.currentSlide.innerHTML}));
        console.log("cur: " + event.currentSlide.innerHTML);
  // event.previousSlide, event.currentSlide, event.indexh, event.indexv
} );
});
