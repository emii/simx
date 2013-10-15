Date: 2013-10-15
Title: Cytokine network
Category: projects
Tags: misc
Template: article_wide
Summary: Cytokine network derived from information collected form COPE database

##The network

<div class="sigma-parent">
<div class="sigma-expand" id="sigma-example">
</div>
</div>
<script src="/static/sigma/sigma.min.js"></script>
<script src="/static/sigma/sigma.parseGexf.js"></script>
<script type="text/javascript">
function init() {
  // Instanciate sigma.js and customize rendering :
  var sigInst = sigma.init(document.getElementById('sigma-example')).drawingProperties({
    defaultLabelColor: '#333',
    defaultLabelSize: 12,
    edgeColor: '#fdf6e3',
    defaultLabelBGColor: '#fff',
    defaultLabelHoverColor: '#000',
    labelThreshold: 5,
    defaultEdgeType: 'curve'
  }).graphProperties({
    minNodeSize: 0.5,
    maxNodeSize: 5,
    minEdgeSize: 2,
    maxEdgeSize: 2,
    sideMargin: 50
  }).mouseProperties({
    maxRatio: 32
  });

  // Parse a GEXF encoded file to fill the graph
  // (requires "sigma.parseGexf.js" to be included)
  sigInst.parseGexf('/static/D3/nt.gexf');

  (function(){
    var popUp;
 
    // This function is used to generate the attributes list from the node attributes.
    // Since the graph comes from GEXF, the attibutes look like:
    // [
    //   { attr: 'Lorem', val: '42' },
    //   { attr: 'Ipsum', val: 'dolores' },
    //   ...
    //   { attr: 'Sit',   val: 'amet' }
    // ]
    function attributesToString(attr) {
      return '<ul>' +
        attr.map(function(o){
          return '<li>Names: ' + o.val + '</li>';
        }).join('') +
        '</ul>';
    }
 
    function showNodeInfo(event) {
      popUp && popUp.remove();
 
      var node;
      sigInst.iterNodes(function(n){
        node = n;
      },[event.content[0]]);
 
      popUp = $(
        '<div class="node-info-popup"></div>'
      ).append(
        // The GEXF parser stores all the attributes in an array named
        // 'attributes'. And since sigma.js does not recognize the key
        // 'attributes' (unlike the keys 'label', 'color', 'size' etc),
        // it stores it in the node 'attr' object :
        attributesToString( node['attr']['attributes'] )
      ).attr(
        'id',
        'node-info'+sigInst.getID()
      ).css({
        'display': 'inline-block',
        'border-radius': 3,
        'padding': 5,
        'background': '#fff',
        'color': '#000',
        'box-shadow': '0 0 4px #666',
        'position': 'absolute',
        'left': node.displayX,
        'top': node.displayY+15
      });
 
      $('ul',popUp).css('margin','0 0 0 20px');
 
      $('#sigma-example').append(popUp);
    }
 
    function hideNodeInfo(event) {
      popUp && popUp.remove();
      popUp = false;
    }
 
    sigInst.bind('overnodes',showNodeInfo).bind('outnodes',hideNodeInfo).draw();
  })();
}

if (document.addEventListener) {
  document.addEventListener("DOMContentLoaded", init, false);
} else {
  window.onload = init;
}
</script>

<style type="text/css">
  /* sigma.js context : */
  .sigma-parent {
    position: relative;
    border-radius: 4px;
    -moz-border-radius: 4px;
    -webkit-border-radius: 4px;
    background: #fafafa;
    height: 800px;
	border:1px #bbb solid;
	width: 80%;
	margin: 0 auto;
  }
  .sigma-expand {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
  }
  .buttons-container{
    padding-bottom: 8px;
    padding-top: 12px;
  }
</style>
