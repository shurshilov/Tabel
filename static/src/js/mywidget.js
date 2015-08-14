openerp.Tabel = function (instance) {
    instance.web.list.columns.add('field.mywidget', 'instance.Tabel.mywidget');
    instance.Tabel.mywidget = instance.web.list.Column.extend({
    init: function () {
        this._super.apply(this, arguments);
	//Get html element by ClassName of openerp date. On my page is 2 date
	//Return [date_start_t,date_end_t]
        var dataView=document.getElementsByClassName('oe_form_field oe_datepicker_root oe_form_field_date');
	//When click button change date element change to picker master
        var dataChange=document.getElementsByClassName('oe_datepicker_master');

	var startDate="0";
	if (dataChange.length >0)
	    startDate=dataChange[0].value
	else
	    if (dataView.length>0)
		startDate = dataView[0].textContent;
	if (startDate!="0"){
	    //Get massive dd.mm.yyyy
	    var arr = startDate.split('.');
	    var d = new Date(arr[2],arr[1]-1,arr[0]);
	    //Get current number of month. From field name delete all chars.
	    var number = this.name.replace(/[A-Za-z]/g, "") - 1;
	    d.setDate(  d.getDate()+ number );

	    //Change name of widget column (attr string)
	    if(d.getDay()>= 0 && d.getDay()<=6)
    	    this.string+=""+["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"][d.getDay()]
	    //this.style.backgroundColor = "red";
//	    for (i in this.widget)
//		this.string=this.string++"\n"
	}
},

    _format: function (row_data, options) {
    //    res = this._super(row_data, options);
        res = this._super.apply(this, arguments);
	var startDate = row_data['time_start_s'].value;
	if (startDate.length>0){
	//Get massive dd.mm.yyyy
	var arr = startDate.split('-');
	var d = new Date(arr[0],arr[1]-1,arr[2]);
	//Get current number of month. From field name delete all chars.
	var number = this.name.replace(/[A-Za-z]/g, "") - 1;
	d.setDate(  d.getDate()+ number );
	if ( d.getDay()==0 || d.getDay()==6)
		    if (res.length>0)
			return "<div class=\"oe_readonly\" style=\" color:#4d394b; background:#eadee0;  \" >" + res+"</div>";
		    else
			return "<div  class=\"oe_readonly\" style=\" color:#4d394b; background:#eadee0;  \" > &nbsp;&nbsp;</div>";
	}
        return res;
	},
    });
    instance.web.list.Handle = instance.web.list.Column.extend({
    init: function () {
        this._super.apply(this, arguments);
        // Handle overrides the field to not be form-editable.
        this.modifiers.readonly = false;
    },
    /**
     * Return styling hooks for a drag handle
     *
     * @private
     */
    _format: function (row_data, options) {
//        return '<div class="oe_list_handle">';
	return '<div  style=\" color:#4d394b; background:#eadee0;  \"> ';
    }
});
      instance.web.ListView.include(/** @lends instance.web.ListView# */{
/*	        resize_fields: function () {
            if (!this.editor.is_editing()) { return; }
            for(var i=0, len=this.fields_for_resize.length; i<len; ++i) {
                var item = this.fields_for_resize[i];
                this.resize_field(item.field, item.cell);
            }
        },
	resize_field: function (field, cell) {

	    field.$el.addClass('oe_readonly');
        },
*/
	 });



};

