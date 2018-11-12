define([
    'dojo/_base/declare',
    'jimu/BaseWidget', 
    'jimu/utils',
    'dojo/_base/html',
    'dojo/dom',

    "esri/Color",
    "esri/symbols/SimpleMarkerSymbol",
    "esri/symbols/SimpleLineSymbol",

    "esri/map",
    "esri/toolbars/draw",
    "esri/toolbars/edit",
    "esri/dijit/editing/Editor",
    "esri/dijit/editing/TemplatePicker",
    "esri/tasks/GeometryService",
    "esri/layers/ArcGISDynamicMapServiceLayer",
    "esri/layers/FeatureLayer",
    "dojo/i18n!esri/nls/jsapi",
    "esri/config",
    "dojo/i18n!esri/nls/jsapi",
    "dojo/_base/array",
    "dojo/keys",
    "dojo/parser",
    "dijit/layout/BorderContainer",
    "dijit/layout/ContentPane",
    "dojo/domReady!"
  ],
  function (declare,
            BaseWidget,
            utils,
            html,
            dom,
            Color, SimpleMarkerSymbol, SimpleLineSymbol,
            Map,
            Draw,
            Edit,
            Editor,
            TemplatePicker,
            GeometryService,
            ArcGISDynamicMapServiceLayer,
            FeatureLayer,
            esriBundle,
            esriConfig,
            jsapiBundle,
            arrayUtils,
            keys,
            parser
  ) {
    return declare([BaseWidget], {

      baseClass: 'HazardMap',
      name: 'HazardMap',

      postCreate: function() {
        this.inherited(arguments);
        self = this;
        console.log('HazardMap::postCreate');
      },

      startup: function() {
        this.inherited(arguments);

        self._createToolbar();
        // Importante para que la barra se encuentre abajo
        this.opLayers = this.map.itemInfo.itemData.operationalLayers;
        // Herramientas de edición para el mapa a generarse
        jsapiBundle.toolbars.draw.start = jsapiBundle.toolbars.draw.start +  "<br>Press <b>ALT</b> to enable snapping";

        esriConfig.defaults.io.proxyUrl = "/proxy/"; //"/proxy/"
        esriConfig.defaults.geometryService = new GeometryService("http://geocatmin.ingemmet.gob.pe/arcgis/rest/services/Utilities/Geometry/GeometryServer");
      },

      // Ejecuta todo en cuanto se abre el widget
      onOpen: function() {
        console.log('HazardMap::onOpen');
        var panel = this.getPanel();
        panel.position.height = 100;
        panel.setPosition(panel.position);
        panel.panelManager.normalizePanel(panel);

        this.widgetActive = true;
        if (this.map.infoWindow.isShowing) {
          this.map.infoWindow.hide();
        }
        this.setPosition();

        self._drawTool()
      },

      // Da la posicion en el footer
      setPosition: function (position, containerNode) {
        if (this.widgetActive) {
          var h = 155;
          this.position = {
            left: 0,
            right: 0,
            bottom: 0,
            height: h,
            relativeTo: "browser"
          };
          var style = utils.getPositionStyle(this.position);
          style.position = 'absolute';
          html.place(this.domNode, window.jimuConfig.layoutId);
          html.setStyle(this.domNode, style);
        }
      },

      _createToolbar: function(){
          _viewerMap.on("layers-add-result", self.initEditing);

      },

      _drawTool: function(){
        var hazardPointLayer = new FeatureLayer("http://geocatmin.ingemmet.gob.pe/arcgis/rest/services/temp/Sistema_peligro_Resiliente/FeatureServer/0", {
          mode: FeatureLayer.MODE_SNAPSHOT,
          outFields: ["*"]
        });
        var hazardLineLayer = new FeatureLayer("http://geocatmin.ingemmet.gob.pe/arcgis/rest/services/temp/Sistema_peligro_Resiliente/FeatureServer/1", {
          mode: FeatureLayer.MODE_SNAPSHOT,
          outFields: ["*"]
        });
        var hazardPolygonLayer = new FeatureLayer("http://geocatmin.ingemmet.gob.pe/arcgis/rest/services/temp/Sistema_peligro_Resiliente/FeatureServer/2", {
          mode: FeatureLayer.MODE_SNAPSHOT,
          outFields: ["*"]
        });
        _viewerMap.addLayers([hazardPointLayer, hazardLineLayer, hazardPolygonLayer]);
        // _viewerMap.addLayers([hazardLineLayer, hazardPolygonLayer]);
      },

      initEditing: function(e) {
        console.log("initEditing", e);
        var currentLayer = null;
        var layers = arrayUtils.map(e.layers, function(l){
          return l.layer;
        });
        console.log("layers", layers);

        var editToolbar = new Edit(_viewerMap);
        editToolbar.on("deactivate", function(evt) {
            currentLayer.applyEdits(null, [evt.graphic], null);
          });

        // Funcionalidades para cada el dibujo de cada poligono
        arrayUtils.forEach(layers, function(layer){
          var editingEneabled = false;
          layer.on("dbl-click", function(evt) {
            event.stop(evt);
            if (editingEnabled === false) {
              editingEnabled = true;
              editToolbar.activate(Edit.EDIT_VERTICES , evt.graphic);
            } else {
              currentLayer = self;
              editToolbar.deactivate();
              editingEnabled = false;
            }
          });

          layer.on("click", function(evt) {
              event.stop(evt);
              if (evt.ctrlKey === true || evt.metaKey === true) { //delete feature if ctrl key is depressed
                layer.applyEdits(null,null,[evt.graphic]);
                currentLayer = self;
                editToolbar.deactivate();
                editingEnabled=false;
              }
            });
        });

        // Barra que contendra a los features a ser editados
        var templatePicker = new TemplatePicker({
          featureLayers: layers,
          grouping: false,
          rows: "1",
          columns: "auto",
          style: "width: 100%; height: auto; overflow: auto; padding: 8px; margin: auto; Color: black;"
        }, "templateDiv");

        templatePicker.startup();

        
        var layerInfos = arrayUtils.map(e.layers, function(l) {
          console.log("l.layer", l.layer);
          return { "featureLayer": l.layer };
        });

        var settings = {
          map: _viewerMap,
          templatePicker: templatePicker,
          layerInfos: layerInfos,
          toolbarVisible: true,
          createOptions: {
            polylineDrawTools: [Editor.CREATE_TOOL_FREEHAND_POLYLINE],
            polygonDrawTools: [ Editor.CREATE_TOOL_FREEHAND_POLYGON,
                Editor.CREATE_TOOL_CIRCLE,
                Editor.CREATE_TOOL_TRIANGLE,
                Editor.CREATE_TOOL_RECTANGLE
              ]
            },
            toolbarOptions: {
              reshapeVisible: true,
              cutVisible: true,
              mergeVisible: true
            }
        };


        var params = { settings: settings };
        var myEditor = new Editor(params, "editorDiv");

        //Propiedades Snap para edicion
        var symbol = new SimpleMarkerSymbol(
            SimpleMarkerSymbol.STYLE_CROSS,
            15,
            new SimpleLineSymbol(
              SimpleLineSymbol.STYLE_SOLID,
              new Color([255, 0, 0, 0.5]),
              5
            ),
            null
          );
        
        var options = {
          snapPointSymbol: symbol,
          tolerance: 20,
          snapKey: keys.ALT
        };
        _viewerMap.enableSnapping(options);

        myEditor.startup();
      },

      _openPrintWidget: function(){
        var widgetsConfig = this.appConfig.widgetPool.widgets;  
        var widgetId;  
        for(var i in widgetsConfig){  
          if(widgetsConfig[i].name == "Print"){  
            widgetId = widgetsConfig[i].id;  
            break;  
          }  
        }  
        var abc = WidgetManager.getInstance().getWidgetsByName("AnchorBarController")[0];  
        abc.setOpenedIds([widgetId]);  
        var printWidget;  
        setTimeout(function(){  
          printWidget = WidgetManager.getInstance().getWidgetById(widgetId);  
          console.info(printWidget);  
        }, 1000);  
      }

    });
  });
