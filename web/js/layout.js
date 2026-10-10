// Presentation changes must preserve LiteGraph's established positional values.
export function arrange(node,first){
 const canonical=[...node.widgets];
 node.widgets=[...first,...canonical.filter(w=>!first.includes(w))];
 const configure=node.onConfigure;
 node.onConfigure=function(info){
  const result=configure?.apply(this,arguments);
  if(info?.widgets_values)canonical.forEach((w,i)=>{if(w.options?.serialize!==false&&i<info.widgets_values.length)w.value=info.widgets_values[i];});
  return result;
 };
 const serialize=node.onSerialize;
 node.onSerialize=function(info){
  const result=serialize?.apply(this,arguments),displayed=info.widgets_values;
  if(displayed)info.widgets_values=[...canonical,...node.widgets.filter(w=>!canonical.includes(w))].map(w=>displayed[node.widgets.indexOf(w)]);
  return result;
 };
}
