odoo.define('theme_alan.s_cat_grid',function(require){
'use strict';

var ajax = require('web.ajax');
var sAnimation = require('website.content.snippets.animation');
const wSaleUtils = require('website_sale.utils');
const { AjaxAddToCart }  = require('theme_alan.core_mixins');
const NavCartUpdate = wSaleUtils.updateCartNavBar;
const cloneAnimation = wSaleUtils.animateClone;

sAnimation.registry.AsCategGrid = sAnimation.Class.extend(AjaxAddToCart, {
    selector: '.as_categ_grid',
    disabledInEditableMode: false,
    'events':{
        'click a.addToCart':'_prodAddToCart',
    },
    start: function (editable_mode) {
        var cr = this;
        if (cr.editableMode){
            cr.$target.empty().append('<div class="container"><div class="seaction-head"><h3>Category Grid Snippet</h3></div></div>');
        }
        if (!cr.editableMode) {
            this.getCatGridData();
        }
    },
    getCatGridData: function() {
        var cr = this;
        ajax.jsonRpc('/get/get_cat_grid_content', 'call', {
            'cat_ids': cr.$target.attr('data-cat-ids'),
            'prod_ids': cr.$target.attr('data-prod-ids'),
            'snippet_type': cr.$target.attr('data-snippet-type'),
            'styleUI': cr.$target.attr('data-styleUI'),
            'dataCount': cr.$target.attr('data-dataCount'),
        }).then(function(data) {
            cr.$target.empty().append(data.grid);
            // var stimer = data.sTimer;
            // var sliderData = { spaceBetween: 15, slidesPerView: 1,
            //     grid: {
            //         rows: 1, 
            //     },
            //     navigation: {
            //       nextEl: ".swiper-button-next",
            //       prevEl: ".swiper-button-prev",
            //     },
            // }
            // if (data.autoSlider) {
            //     sliderData.autoplay = {
            //       delay: stimer,
            //       disableOnInteraction: false,
            //     }
            // }
            // if (data.infinity) {
            //     sliderData['loop'] = true
            // }
            // cr.initializeSwiper(sliderData);
        });
    },
    // initializeSwiper: function(data){
    //     var $slider = this.$target.find(".as-Swiper");
    //     $slider.attr("id","cr-swiper");
    //     var swiper = new Swiper("#cr-swiper", data);
    //     $slider.removeAttr("id");
    // },

    _prodAddToCart: function(ev){
        var product_id = parseInt($(ev.currentTarget).attr('data-product-product-id'));
        this._alanAddToCart({"product_id" : product_id, "add_qty":1}).then(data =>{
            cloneAnimation($('header .o_wsale_my_cart').first(), this.$(ev.currentTarget).closest('form').find('.as-product-img'), 25, 40);
            NavCartUpdate(data);
        })
    },
});
});