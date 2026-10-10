import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('../web/js/layout.js',import.meta.url),'utf8');
const {arrange}=await import('data:text/javascript,'+encodeURIComponent(source));
const parameters=[{name:'model',value:'d1'},{name:'prompt',value:'lake'},{name:'seed',value:42}];
const transport={name:'transport',options:{serialize:false}},preview={name:'result',options:{serialize:false}};
const node={widgets:[...parameters,transport,preview]};arrange(node,[transport,preview]);
assert.deepEqual(node.widgets.map(w=>w.name),['transport','result','model','prompt','seed']);
const info={widgets_values:node.widgets.map(w=>w.value)};node.onSerialize(info);
assert.deepEqual(info.widgets_values.slice(0,3),['d1','lake',42]);
// Model LiteGraph's positional assignment before invoking onConfigure.
node.widgets.forEach((w,i)=>w.value=info.widgets_values[i]);node.onConfigure(info);
assert.deepEqual(parameters.map(w=>w.value),['d1','lake',42]);
console.log('Display ordering preserves saved model, prompt and seed values');
