<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34" styleCategories="Symbology|Labeling">
  <renderer-v2 type="graduatedSymbol" attr="surface_temp_c" graduatedMethod="GraduatedColor">
    <ranges>
      <range lower="28" upper="31" symbol="0" label="28-31°C (Cool)" render="true"/>
      <range lower="31" upper="33" symbol="1" label="31-33°C (Mild)" render="true"/>
      <range lower="33" upper="35" symbol="2" label="33-35°C (Warm)" render="true"/>
      <range lower="35" upper="37" symbol="3" label="35-37°C (Hot)" render="true"/>
      <range lower="37" upper="42" symbol="4" label="37-42°C (Extreme)" render="true"/>
    </ranges>
    <symbols>
      <symbol name="0" type="fill"><layer class="SimpleFill">
        <prop k="color" v="49,54,149,180"/><prop k="outline_color" v="50,50,50,80"/><prop k="outline_width" v="0.2"/>
      </layer></symbol>
      <symbol name="1" type="fill"><layer class="SimpleFill">
        <prop k="color" v="116,173,209,180"/><prop k="outline_color" v="50,50,50,80"/><prop k="outline_width" v="0.2"/>
      </layer></symbol>
      <symbol name="2" type="fill"><layer class="SimpleFill">
        <prop k="color" v="254,224,144,180"/><prop k="outline_color" v="50,50,50,80"/><prop k="outline_width" v="0.2"/>
      </layer></symbol>
      <symbol name="3" type="fill"><layer class="SimpleFill">
        <prop k="color" v="253,174,97,180"/><prop k="outline_color" v="50,50,50,80"/><prop k="outline_width" v="0.2"/>
      </layer></symbol>
      <symbol name="4" type="fill"><layer class="SimpleFill">
        <prop k="color" v="215,48,39,200"/><prop k="outline_color" v="50,50,50,80"/><prop k="outline_width" v="0.2"/>
      </layer></symbol>
    </symbols>
  </renderer-v2>
</qgis>
