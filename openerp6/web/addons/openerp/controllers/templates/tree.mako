<%inherit file="/openerp/controllers/templates/base_dispatch.mako"/>

<%def name="header()">
    <script type="text/javascript" src="/openerp/static/javascript/treeview.js"></script>
    
    <script type="text/javascript">
        var RESOURCE_ID = '${rpc.get_session().active_id}';
    </script>
    
    % if can_shortcut:
        <script type="text/javascript">
            jQuery(document).ready(function () {
                jQuery('#shortcut_add_remove').click(toggle_shortcut);
            });
        </script>
    % endif
</%def>

<%def name="content()">
    <%
        if can_shortcut:
            if rpc.get_session().active_id in shortcut_ids:
                shortcut_class = "shortcut-remove"
            else:
                shortcut_class = "shortcut-add"
    %>
    <table id="treeview" class="view" width="100%" border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td width="100%" valign="top">
            	% if tips:
                    <div id="help-tips">
                        <p>${tips}</p>
                        <a href="/openerp/form/close_or_disable_tips" id="disable-tips" style="text-decoration: underline;">${_("Disable all Tips")}</a>
                        <a href="#hide" id="hide-tips" style="text-decoration: underline;">${_("Hide this Tip")}</a>
                        <br style="clear: both"/>
                    </div>
                % endif
                <div id="body_form">
	                <h1>
	                    % if can_shortcut:
	                        <a id="shortcut_add_remove" title="${_('Add / Remove Shortcut...')}" href="javascript: void(0)" class="${shortcut_class}"></a>
	                    % endif
	                    ${tree.string}
	                </h1>
	                <div>
	                    % if tree.toolbar:
	                    <div>
	                        <select id="treeview-tree-selector">
	                            % for tool in tree.toolbar:
	                                <option value="${tool['id']}" data-ids="${tool['ids']}">
	                                    ${tool['name']}
	                                </option>
	                            % endfor
	                        </select>
	                    </div>
	                    % endif
	                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
	                        <tr>
	                            <td width="100%" valign="top" class="tree_grid">${tree.display()}</td>
	                        </tr>
	                    </table>
	                </div>
            	</div>
            </td>
                % if tree.sidebar:
                    <td id="main_sidebar" valign="top">
	                    <a class="toggle-sidebar closed" href="javascript:void(0)">Toggle</a>
	                    <div id="tertiary" class="closed">
	                        <div id="tertiary_wrap">
	                            ${tree.sidebar.display()}
	                        </div>
	                    </div>
	                </td>
	                <script type="text/javascript">
	                    jQuery('.toggle-sidebar').toggler('#tertiary', function (){
	                        jQuery(window).scrollLeft(
	                            jQuery(document).width() - jQuery(window).width());
	                    });
	                </script>
                % endif
        </tr>
    </table>
    
    <script type="text/javascript">
        var TREEVIEW = new TreeView(${tree.id});
    </script>

    <script type="text/javascript">
        jQuery(document).ready(function () {
            var $hide = jQuery('#hide-tips').click(function () {
                jQuery('#help-tips').hide();
                return false;
            });
            jQuery('#disable-tips').click(function () {
                jQuery.post(this.href);
                $hide.click();
                return false;
            })
        })
    </script>
    
</%def>
