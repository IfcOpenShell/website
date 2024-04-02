(function($) {
    'use strict';

    /**<<=== 01 Mobile Menu JS ==>>**/
    $('#mobile-menu-active').mobileMenus();
    $('#mobile-menu-active .has-children > a').on('click', function(e) {
        e.preventDefault();
    });

    $(".mobile-menu").on("click", function(e) {
        e.preventDefault();
        $(".menu-slide-bar").toggleClass("show");
        $("body").addClass("on-side");
        $('.body-overlay').addClass('active');
        $(this).addClass('open');
    });

    $(".close-mobile-menu > a").on("click", function(e) {
        e.preventDefault();
        $(".menu-slide-bar").removeClass("show");
        $("body").removeClass("on-side");
        $('.body-overlay').removeClass('active');
        $('.mobile-menu').removeClass('open');
    });

    $('.body-overlay').on('click', function() {
        $(this).removeClass('active');
        $(".menu-slide-bar").removeClass("show");
        $("body").removeClass("on-side");
        $('.mobile-menu').removeClass('open');
    });

    /**<<=== 02 Header Sticky JS ==>>**/
    $(window).on('scroll', function() {
        if ($(this).scrollTop() > 150) {
            $('.navbar').addClass("is-sticky");
        } else {
            $('.navbar').removeClass("is-sticky");
        };
    });

    /**<<=== 06 Back To Top JS ==>>**/
    $('.back-to-top').on('click', function() {
        $("html, body").animate({
            scrollTop: "0"
        }, 50);
    });
    $(window).on('scroll', function() {
        var scrolled = $(window).scrollTop();
        if (scrolled > 300) $('.back-to-top').addClass('active');
        if (scrolled < 300) $('.back-to-top').removeClass('active');
    });

    /**<<=== 07 Preloader JS ==>>**/
    $(window).on('load', function() {
        $('.preloader').addClass('preloader-deactivate');
    })

    /**<<=== 08 WOW JS ==>>**/
    if ($('.wow').length) {
        var wow = new WOW({
            mobile: false
        });
        wow.init();
    }

    /**<<=== 15 Curt BTN JS ==>>**/
    $(".minus").click(function() {
        var $input = $(this).parent().find(".box");
        var count = parseInt($input.val()) - 1;
        count = count < 1 ? 1 : count;
        $input.val(count);
        $input.change();
        return false;
    });
    $(".plus").click(function() {
        var $input = $(this).parent().find(".box");
        $input.val(parseInt($input.val()) + 1);
        $input.change();
        return false;
    });

    $(document).ready(function() {
        $('.owl-carousel').owlCarousel({
            items: 1,
            loop: true,
            nav: true,
            center: true,
            margin: 10,
            callbacks: true,
            URLhashListener: true,
            autoplay: true,
            autoplayTimeout: 3000,
            autoplayHoverPause: true,
            // startPosition: 'URLHash'
        });
    });

    const progressBar = document.getElementById("progress-bar");
    let statusVal = 0;
    let id = null;
    let speed = 50;
    let maxPercent = 50;

    id = setInterval(() => {
        updateProgressBar();
    }, speed);

    function updateProgressBar() {
        const isMaxVal = statusVal >= maxPercent;

        if (isMaxVal) {
            clearInterval(id);
            statusVal = 0;

            return setTimeout(() => {
                id = setInterval(() => {
                    updateProgressBar();
                }, speed);
            }, 2000);
        }

        statusVal++;
        progressBar.dataset.status = statusVal + "%";
        progressBar.setAttribute(
            "style",
            `--__progress-bar__status_wh: ${statusVal}%;`
        );
    };

    fetch('https://opencollective.com/opensourcebim.json').then(r => r.json()).then(d => {
        let monthly = d.yearlyIncome / 12 / 100.;
        let percentage = monthly / 2500 * 100;
        var amountRaisedElements = document.getElementsByClassName('amount-raised');
        for (var i = 0; i < amountRaisedElements.length; i++) {
            amountRaisedElements[i].textContent = '$' + monthly.toFixed(0);
        }
        document.documentElement.style.setProperty('--percentage-raised', percentage + '%');
        maxPercent = percentage.toFixed(0);
    });



    //  Home page Tab section
    var tab;
    var tabContent;

    window.onload = function() {
        tabContent = document.getElementsByClassName('tabContent');
        tab = document.getElementsByClassName('tab');
        hideTabsContent(1);
    }

    var tabs = document.getElementById('tabs');
    if (tabs) {
        tabs.onclick = function(event) {
            var target = event.target;
            if (target.className == 'tab') {
                for (var i = 0; i < tab.length; i++) {
                    if (target == tab[i]) {
                        showTabsContent(i);
                        break;
                    }
                }
            }
        }
    }

    function hideTabsContent(a) {
        for (var i = a; i < tabContent.length; i++) {
            tabContent[i].classList.remove('show');
            tabContent[i].classList.add("hide");
            tab[i].classList.remove('whiteborder');
        }
    }

    function showTabsContent(b) {
        if (tabContent[b].classList.contains('hide')) {
            hideTabsContent(0);
            tab[b].classList.add('whiteborder');
            tabContent[b].classList.remove('hide');
            tabContent[b].classList.add('show');
        }
    }
    //  Home page Tab section


    // community page code
    function loadRSS(callback) {
        var xobj = new XMLHttpRequest();
        xobj.overrideMimeType('application/xml');
        xobj.open('GET', 'assets/v0.7.0.atom', true);
        xobj.onreadystatechange = function() {
            if (xobj.readyState == 4 && xobj.status == '200') {
                callback(xobj.responseText);
            }
        };
        xobj.send(null);
    }
    loadRSS(function(response) {
        var parser = new DOMParser();
        var xmlDoc = parser.parseFromString(response, 'text/xml');
        var entries = xmlDoc.getElementsByTagName('entry');
        var liTemplate = '<li><img src="_THUMBNAIL_" class="post-thumbnail" alt="Avatar" /><p class="post-paragraph"><a href="_LINK_">_TITLE_</a> by <a href="_AUTHORURL_"><span class="author-name">@_AUTHORNAME_</span></a> <span class="post-date">_UPDATED_</span></p></li>'
        var commits = document.getElementById('commits');
        if (!commits) {
            return;
        }
        for (var i = 0; i < 10; i++) {
            console.log(entries[i].getElementsByTagName('link')[0].getAttribute('href'));
            console.log(entries[i].getElementsByTagName('link')[0]);
            var data = {
                '_TITLE_': entries[i].getElementsByTagName('title')[0].textContent,
                '_UPDATED_': entries[i].getElementsByTagName('updated')[0].textContent.split('T')[0],
                '_LINK_': entries[i].getElementsByTagName('link')[0].getAttribute('href'),
                '_THUMBNAIL_': entries[i].getElementsByTagName('media:thumbnail')[0].getAttribute('url'),
                '_AUTHORNAME_': entries[i].getElementsByTagName('author')[0].getElementsByTagName('name')[0].textContent ? entries[i].getElementsByTagName('author')[0].getElementsByTagName('name')[0].textContent : entries[i].getElementsByTagName('author')[0].getElementsByTagName('email')[0].textContent,
                '_AUTHORURL_': entries[i].getElementsByTagName('author')[0].getElementsByTagName('uri').length ? entries[i].getElementsByTagName('author')[0].getElementsByTagName('uri')[0].textContent : 'mailto:' + entries[i].getElementsByTagName('author')[0].getElementsByTagName('email')[0].textContent
            };
            var innerHTML = liTemplate;
            for (var key in data) {
                innerHTML = innerHTML.replace(key, data[key]);
            }
            var li = document.createElement('li');
            li.innerHTML = innerHTML;
            commits.appendChild(li);
        }
    });
})(jQuery);
