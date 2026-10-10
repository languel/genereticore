"""Build image demos offline from checked-in companion source templates.

Pass the public Genereti checkout. No model download or running Comfy is needed.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('genereti', type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
base=args.genereti/'example_workflows'
source_code='''function setup(){createCanvas(windowWidth,windowHeight);}
function draw(){
 background(255); noFill(); stroke(0); strokeWeight(7);
 const t=frameCount*0.015;
 ellipse(width*0.5+sin(t)*width*0.08,height*0.45,width*0.48,height*0.5);
 rect(width*0.18,height*0.7,width*0.64,height*0.13,12);
}'''
prompt='A luminous abstract performance stage made from hand-cut paper shapes, cobalt blue and orange light, energetic theatrical composition'
for number,kind,turbo in [(9,'Livecode',False),(10,'Drawing',False),(11,'Livecode',True),(12,'Drawing',True)]:
 template=json.loads((base/('ꘇ-Livecode-Realtime.json' if kind=='Livecode' else 'ꘇ-Drawing-Source.json')).read_text())
 source=deepcopy(template['nodes'][0]);source['id']=1;source['pos']=[0,330];source['title']='ꘇ '+kind.lower()+' · live sketch';source['order']=0
 if kind=='Livecode':
  source['widgets_values']=['p5',256,256,True,source_code,'{}','Live']
  source['properties']['generetiLivecodeLastGood']={'mode':'p5','source':source_code}
 for output in source['outputs']:output['links']=[]
 viewer=deepcopy(template['nodes'][1]);viewer.update(id=3,pos=[1100,330],order=2,title='ꘇ image preview · latest completed image')
 viewer['inputs'][0]['link']=2;viewer['outputs'][0]['links']=[]
 viewer['widgets_values']=[512,'Live'];viewer['widgets_values_named']={'preview_size':512,'genereti_delivery':'Live'}
 typ='GeneretiSDTurboGenerate' if turbo else 'GeneretiSDXSGenerate'
 values={'model_path':'256/turbo_unet.mlpackage' if turbo else '256/unet.mlpackage','prompt':prompt,'mode':'canny' if turbo else 'sketch','seed':42}
 if turbo:values.update(preprocess=True,strength=.65)
 values.update(control_scale=1.,invert=False,movement=0.)
 saved=[]
 for name,value in values.items():
  saved.append(value)
  if name=='seed':saved.append('fixed')
 saved.append('Live')
 inputs=[{'name':'image','type':'IMAGE','link':1}]
 generator={'id':2,'type':typ,'title':'ꘅ '+('SD Turbo' if turbo else 'SDXS')+' generator','pos':[650,330],'size':[410,420],'flags':{},'order':1,'mode':0,'inputs':inputs,'outputs':[{'name':'image','type':'IMAGE','links':[2]},{'name':'metrics','type':'STRING','links':[3]}],'properties':{'Node name for S&R':typ,'genereti_widget_values':values,'genereti_live_prompt':True,'genereti_applied_prompt':prompt},'widgets_values':saved,'widgets_values_named':{**values,'genereti_delivery':'Live'}}
 metrics={'id':4,'type':'GeneretiCoreResult','title':'ꘅ Text / JSON Viewer · queued timings','pos':[650,820],'size':[410,240],'flags':{},'order':3,'mode':0,'inputs':[{'name':'text','type':'STRING','link':3}],'outputs':[],'properties':{'Node name for S&R':'GeneretiCoreResult'},'widgets_values':[]}
 note={'id':5,'type':'Note','title':'Start here · '+kind+' → '+('SD Turbo' if turbo else 'SDXS'),'pos':[0,0],'size':[1500,290],'flags':{},'order':4,'mode':0,'properties':{},'widgets_values':[f'''Experimental local image demo. Requires updated Genereti + GeneretiCore companion bridge. Native inference: macOS 14+ Apple silicon, optional image dependencies and existing converted bundles. No weights included. Do not enable the legacy genereti_comfy_coreml pack at the same time.
1. Choose your installed model_path on the ꘅ generator. {'Draw bold shapes on ꘇ drawing (transparent paper composites on white).' if kind=='Drawing' else 'The authored ꘇ livecode sketch can render independently; use its editor Run if needed.'}
2. Leave source, generator and image preview in Live. Press the generator ▶ explicitly. Opening this workflow never starts inference. The viewer holds the last completed image during computation.
3. Change one source shape or prompt. Generator Ⅱ pauses new inference; a running native call finishes and its stale output is discarded. Preview freeze/minimize only changes local display.
4. For one frame, switch generator to Comfy Queue and press Comfy Run. The queued image and metrics update through their wires. Metrics below describe queued work; live timings appear in the generator status.
5. ? opens authored reference. On the image preview use Alt-O for visual view or Alt-W for overlay. Models remain local; no cloud fallback.
This migration and its model workflows have not been exercised on Mac. See docs/realtime-image-demo.md.''']}
 source['outputs'][0]['links']=[1]
 graph={'last_node_id':5,'last_link_id':3,'nodes':[source,generator,viewer,metrics,note],'links':[[1,1,0,2,0,'IMAGE'],[2,2,0,3,0,'IMAGE'],[3,2,1,4,0,'STRING']],'groups':[],'config':{},'extra':{'ds':{'scale':.6,'offset':[60,60]}},'version':.4}
 name=f'{number:02} - {kind} to '+('SD Turbo' if turbo else 'SDXS')+'.json'
 (root/'example_workflows'/name).write_text(json.dumps(graph,indent=2,ensure_ascii=False)+'\n')
