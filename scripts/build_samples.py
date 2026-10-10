"""Build reproducible teaching graphs from the active Comfy and companion schemas."""
import json
from pathlib import Path
import urllib.request
import uuid
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from genereticore.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

COMPANION_LABELS = {'GeneretiLivecode': 'ꘇ livecode', 'GeneretiLiveImagePreview': 'ꘇ image preview', 'GeneretiDatLesson': 'ꘇ lesson'}
ROOT = Path(__file__).resolve().parents[1]
with urllib.request.urlopen('http://127.0.0.1:8003/object_info') as response:
    INFO = json.load(response)
for name, cls in NODE_CLASS_MAPPINGS.items():
    INFO[name] = {'input': cls.INPUT_TYPES(), 'output': cls.RETURN_TYPES,
                  'output_name': getattr(cls, 'RETURN_NAMES', cls.RETURN_TYPES)}

CONCEPTS = {
 '00-start': 'DEMO: Read the result contract, without AI. The Decision Scores Validator checks supplied example numbers and the selected label. The Text / JSON Viewer displays the validated answer. We supplied these scores; they were not inferred. Blue and orange are allowed labels. Editing the fixture tests consistency, not training. Read Tutorial 0 first.',
 '01-text': 'DEMO: Generate an artwork title. Local Text reads a prompt and writes a short response using Qwen. Follow text to the Text / JSON Viewer; metrics reports timing. This is word generation, not a fixed-option decision.',
 '02-decision': 'DEMO: Ask Qwen for a bounded palette decision. A situation plus question and two allowed labels become a selected label and distribution. Unlike the supplied-score exercise, the model produces these scores. Keep labels unchanged; edit the situation to compare answers.',
 '03-vision': 'DEMO: Describe one image. Empty Image provides a synthetic blue square; Local Vision reads its pixels and prompt, then sends a description to the viewer. This is image analysis, not image generation or palette selection.',
 '04-genereti-vision': 'DEMO: Observe a changing artwork. Genereti Livecode renders an authored orange circle; Local Vision analyzes one queued frame. The viewer displays its description. Rendering continues independently; no automatic per-frame inference occurs.',
 '05-genereti-palette': 'DEMO: Use a bounded Qwen decision as a creative control. Local Decision selects blue or orange; Choice to Value maps that label to a numeric hue; Genereti Livecode applies it to a moving circle. The model never writes executable code.',
 '07-d1': 'DEMO: A specialist decision model controls an artwork. d1 reads a text state, question and allowed palette labels in one Core ML pass with zero generated tokens. Choice to Value translates the selected label into paletteHue; p5 renders the authored circle. Inspect the distribution and timing viewers. This d1 conversion is text-only.'
}
RENAMES = {
 '00 - Start here - no model.json':'01 - Read a decision - no model.json',
 '01 - Local text.json':'02 - Local text.json',
 '02 - Local decisions.json':'03 - Local decisions.json',
 '03 - Local vision.json':'04 - Local vision.json',
 '04 - Genereti - sketch to vision walkthrough.json':'05 - Genereti - sketch to vision walkthrough.json',
 '05 - Genereti - AI palette walkthrough.json':'06 - Genereti - AI palette walkthrough.json'
}
class Graph:
    def __init__(self, slug, title, instructions):
        self.slug, self.title = slug, title
        self.nodes, self.links = [], []
        self.nodes.append({'id':1,'type':'Note','title':'Start here · '+title,'pos':[0,0], 'size':[800,310],
            'flags':{},'order':0,'mode':0,'properties':{},'widgets_values':[CONCEPTS.get(slug, '') + '\n\n' + instructions]})
    def node(self, kind, title, pos, size=(360,400), **values):
        schema = INFO[kind]; inputs=[]; widgets=[]; named={}
        for group in ('required','optional'):
            for name, definition in schema['input'].get(group,{}).items():
                typ=definition[0]; options=definition[1] if len(definition)>1 else {}
                if typ=='COMFY_AUTOGROW_V3': continue
                widget=isinstance(typ,list) or typ in ('COMBO','STRING','INT','FLOAT','BOOLEAN') and not options.get('forceInput')
                if widget:
                    choices=typ if isinstance(typ,list) else options.get('options',[])
                    value=values.get(name, options.get('default',choices[0] if choices else None))
                    widgets.append(value); named[name]=value
                if not options.get('socketless'):
                    inputs.append({'name':name,'type':'COMBO' if isinstance(typ,list) else typ,'link':None,
                                   **({'widget':{'name':name}} if widget else {})})
        id=len(self.nodes)+1
        props={'Node name for S&R':kind,'generetiLessonRef':str(uuid.uuid5(uuid.NAMESPACE_URL,self.slug+str(id))),
               'genereti_widget_values':named}
        if kind in ('GeneretiLivecode','GeneretiLiveImagePreview','GeneretiDatLesson'):
            widgets.append('Live'); named['genereti_delivery']='Live'
        node={'id':id,'type':kind,'title':NODE_DISPLAY_NAME_MAPPINGS.get(kind, COMPANION_LABELS.get(kind, kind)) + ' · ' + title.replace('ꘇ ',''),'pos':[pos[0],pos[1]+120],'size':list(size),'flags':{},'order':id-1,'mode':0,
              'inputs':inputs,'outputs':[{'name':name.lower() if kind.startswith('Genereti') else name,'type':typ,'links':[]} for name,typ in zip(schema['output_name'],schema['output'])],
              'properties':props,'widgets_values':widgets,'widgets_values_named':named}
        self.nodes.append(node); return node
    def connect(self, source, target, input, output=0):
        slot=next(i for i,p in enumerate(target['inputs']) if p['name']==input)
        id=len(self.links)+1
        target['inputs'][slot]['link']=id; source['outputs'][output]['links'].append(id)
        self.links.append([id,source['id'],output,target['id'],slot,source['outputs'][output]['type']])
    def result(self, source, output=0, pos=(840,260), title='Read the result'):
        target=self.node('GeneretiCoreResult',title,pos,(430,220)); self.connect(source,target,'text',output);return target
    def livecode(self, pos=(0,270), controlled=False):
        code='''let paletteHue = 210; /* 0..360 */
function setup(){ createCanvas(windowWidth,windowHeight); colorMode(HSB,360,100,100); }
function draw(){
  background(210,85,35); noStroke(); fill(paletteHue,85,100);
  circle(width/2 + sin(frameCount*0.025)*width*0.12,height/2,min(width,height)*0.45);
}'''
        if not controlled: code=code.replace('let paletteHue = 210;', 'let paletteHue = 30;')
        node=self.node('GeneretiLivecode','ꘇ moving circle · press editor Run',pos,(410,650),
            language='p5',width=320,height=240,auto_update=True,code=code,parameters=json.dumps({'paletteHue':210 if controlled else 30}),performance='{}')
        node['properties']['generetiLivecodeParameters']={'values':{'paletteHue':210 if controlled else 30},'slots':{'paletteHue':0}}
        node['properties']['generetiLivecodeLastGood']={'mode':'p5','source':code}
        node['inputs'].append({'name':'controls.value0','type':'FLOAT','label':'paletteHue','link':None,'widget':{'name':'controls.value0'}})
        return node
    def lesson(self, steps):
        guide={'format':'genereti-guide','version':1,'id':'genereticore-'+self.slug,'title':self.title,'summary':'Learn on this editable graph. Inference starts only when you press Run.', 'steps':[]}
        for title,text,node,part in steps:
            guide['steps'].append({'title':title,'text':node['title'] + '\n\n' + text,'target':{'nodeType':node['type'],'nodeId':node['id'],'ref':node['properties']['generetiLessonRef'],'part':part}, 'hint':'Follow the note at the top of the workflow. Top Run updates connected nodes.'})
        lesson=self.node('GeneretiDatLesson','ꘇ walkthrough · press its Run',(0,1420),(600,500),guide=json.dumps(guide,ensure_ascii=False,indent=2))
        lesson['properties']['generetiLessonStartup']='manual'
    def save(self, name):
        name = RENAMES.get(name, name)
        self.nodes[0]['widgets_values'][0] += '\n\nNodes in this demo:\n' + '\n'.join(n['title'] for n in self.nodes[1:])
        graph={'last_node_id':len(self.nodes),'last_link_id':len(self.links),'nodes':self.nodes,'links':self.links,'groups':[], 'config':{},'extra':{'ds':{'scale':.7,'offset':[70,70]}},'version':.4}
        (ROOT/'example_workflows'/name).write_text(json.dumps(graph,indent=2,ensure_ascii=False)+'\n')

q='Press the top Run button (or ▷ on the inference node). Follow the wires to the result. ϟ only previews locally on the inference node; it does not update connected nodes.'
g=Graph('00-start','No model needed','1. Press top Run. The validator checks the supplied fixture.\n2. Open scores in the viewer Tree mode. Blue has the larger score and is selected.\n3. Optional experiment: change blue to 0.1, keep orange at 0.2, AND change "choice":"blue" to "choice":"orange" in the same JSON. Run again: orange wins. Editing scores alone does not update choice.\n4. The scores need not sum to 1. The viewer normalizes 0.1/0.2 to about 0.333/0.667. This checks a supplied answer; it does not train a model. In model demos, edit the situation instead.')
a=g.node('GeneretiCoreValidateDecision','supplied decision fixture (no AI)',(0,260));g.result(a,1,title='2 · normalized scores');g.result(a,0,(840,520),'3 · selected choice');g.save('00 - Start here - no model.json')
g=Graph('01-text','Your first local text','1. On local text, click ↓ only if the model is missing. Wait for installed.\n2. '+q+'\n3. Change the prompt and Run again.\nA small model can give incorrect answers; this is an integration demo.')
a=g.node('GeneretiCoreText','1 · prompt and local model',(0,260),prompt='Suggest one short title for an artwork about an orange circle on a blue field. /no_think',max_tokens=96);g.result(a);g.result(a,1,(840,520),'Timing and model');g.save('01 - Local text.json')
g=Graph('02-decision','Choose from fixed options','1. Download Qwen 0.6B with ↓ if missing.\n2. '+q+'\n3. Change the scene in prompt and compare the scores.\nThe model picks only a listed option. Scores are uncalibrated and the choice may be poor. No generated code runs.')
a=g.node('GeneretiCoreDecision','1 · describe a scene',(0,260));g.result(a,0,title='2 · selected palette');g.result(a,1,(840,520),'3 · scores and distribution');g.save('02 - Local decisions.json')
g=Graph('03-vision','Analyze an image','1. Download Qwen3-VL 2B with ↓ on local vision if missing (about 3.3 GB).\n2. Press top Run. The image source is a solid blue fixture; its description appears on the right.\n3. Replace Empty Image with your own Load Image and connect IMAGE to local vision.image.\nVision reads one queued image. No camera or upload is started.')
a=g.node('EmptyImage','1 · synthetic blue image',(0,260),(320,220),width=256,height=256,batch_size=1,color=0x0040DC)
b=g.node('GeneretiCoreVision','2 · describe this image',(390,260),prompt='Describe the dominant color briefly.',max_tokens=64)
g.connect(a,b,'image');g.result(b,pos=(840,260));preview=g.node('PreviewImage','Image being analyzed',(0,540),(320,300));g.connect(a,preview,'images');g.save('03 - Local vision.json')
g=Graph('04-genereti-vision','Genereti sketch to local vision','Requires Genereti public + GeneretiCore.\n1. The saved sketch starts moving on open; use editor Run after code edits.\n2. Download Qwen3-VL 2B on local vision if missing.\n3. Press TOP Run to sample one frame and analyze it. The animation keeps moving while AI works.\n4. Change circle hue or motion in the editor and Run again.\nFor guided steps, scroll down to the walkthrough node and press its Run.')
a=g.livecode();b=g.node('GeneretiCoreVision','ꘇ inspect one queued frame',(470,270),prompt='Describe the shapes and colors in one sentence.',max_tokens=64);g.connect(a,b,'image');r=g.result(b,pos=(940,270))
g.lesson([('Start the artwork','The saved sketch starts on open. Use editor Run after edits; an orange circle moves on blue.',a,'code'),('Prepare the local model','Click ↓ if the vision model is missing. No frame is sent to cloud inference.',b,'toolbar'),('Sample a frame','Press the TOP Comfy Run. It captures one frame from p5 and submits local analysis.',a,'preview'),('Read the answer','Read the result. Edit the p5 color and queue a second observation. Animation and inference have separate clocks.',r,'node')]);g.save('04 - Genereti - sketch to vision walkthrough.json')
g=Graph('05-genereti-palette','A model chooses an artwork palette','Requires Genereti public + GeneretiCore.\n1. The saved artwork starts on open; use editor Run after code edits.\n2. Download Qwen 0.6B on local decision if missing.\n3. Press TOP Run: the model chooses blue/orange; the map turns that label into a hue, which drives p5.\n4. Change the scene prompt and Run again.\nThe small model can choose poorly. The graph maps allowed labels to numbers; it never executes model-written code.\nScroll down and Run the walkthrough for guided steps.')
a=g.node('GeneretiCoreDecision','ꘇ choose a palette',(0,270),prompt='An energetic warm sunrise performance. Choose the palette that fits.',max_tokens=128)
b=g.node('GeneretiCoreChoiceValue','ꘇ palette label → hue',(420,270),(320,220));g.connect(a,b,'choice')
c=g.livecode((810,270),True);g.connect(b,c,'controls.value0');r=g.result(a,1,(0,720),'Model scores · inspect the choice')
preview=g.node('GeneretiLiveImagePreview','ꘇ live artwork',(1280,270),(400,480),preview_size=320);g.connect(c,preview,'image')
g.lesson([('Start the scene','The saved artwork starts on open, with paletteHue at 210 (blue).',c,'code'),('Ask for a palette','Edit the scene description, then press TOP Run. Inference starts only on that action.',a,'parameter'),('Follow the typed control','The choice label maps to 210 or 30. That numeric wire drives the p5 hue parameter.',b,'node'),('Inspect the answer','Read the scores and compare the artwork. Try a different prompt; no model-written code is evaluated.',r,'node')]);g.save('05 - Genereti - AI palette walkthrough.json')
g=Graph('tutorial-0', 'What is a decision model?', 'READ FIRST: We are building a moving artwork that responds to a described scene. A decision model reads a state and question, ranks allowed labels, and returns a distribution. A separate authored map converts the selected label to a creative control.\nOpen Tutorial 0 with the book button below. It explains the theory, each node type, why choices are authored, and how to read results. No model or download is needed.')
g.node('GeneretiCoreTutorial','read the introduction',(0,370),(550,200));g.save('00 - Tutorial 0 - decision models.json')
g=Graph('07-d1','d1 scene to artwork palette','Requires Genereti public. The artwork starts on open, but inference waits for top Run.\n1. Download d1 with ↓ if missing. First Run compiles/loads locally.\n2. Run and inspect choice, probabilities and metrics in Tree mode.\n3. Change only the state to: The scene is entirely orange: orange lights, orange walls and an orange sunset. Run again and compare. Then try a warm festival description; subjective choices may surprise you.\n4. Keep the blue/orange options unchanged for this experiment. They define our two authored palettes. Use the mapping node to choose different numeric hues.')
a=g.node('GeneretiCoreDecision','state → allowed palette',(0,370),(420,560),model='d1-omni-600m',prompt='A quiet moonlit lake with soft ripples and a cool evening breeze.',question='Which color palette best fits this scene?',choices_json='["blue", "orange"]')
b=g.node('GeneretiCoreChoiceValue','palette label → hue',(480,370),(340,260));g.connect(a,b,'choice')
c=g.livecode((890,370),True);g.connect(b,c,'controls.value0')
r=g.result(a,1,(0,1020),'decision distribution');g.result(a,2,(480,1020),'cold / warm request metrics')
preview=g.node('GeneretiLiveImagePreview','authored artwork',(1370,370),(400,480),preview_size=320);g.connect(c,preview,'image')
g.lesson([('Read the decision inputs','The state describes the scene. The question asks for a palette. The two labels are allowed answers, not instructions to change scores.',a,'parameter'),('Run one local decision','Press top Run. d1 evaluates options without generating text. Download is separate; first inference compiles and loads.',a,'toolbar'),('Follow the creative mapping','The selected label maps to a hue number. This authored map, not model-written code, controls paletteHue.',b,'node'),('Compare two situations','Read the distribution, then edit only the state to an entirely orange scene and Run again. Compare the palette. Try an ambiguous warm festival next and critique the decision.',r,'node')]);g.nodes[-1]['pos']=[0,1480];g.save('07 - d1 - scene to artwork palette.json')
g=Graph('08-arcade','Blocks & Beats · a decision arcade','DEMO: A self-playing simplified Tetris game conducts an authored soundtrack. Open ꘅ Decision Arcade with ▦. In its page, the board rules shortlist four legal drops, d1 chooses one, and a separate d1 decision chooses calm/drive/tense/celebrate music. The game applies only validated labels. The renderer and audio scheduler run independently of the bounded local inference worker.\n1. Read Tutorial 8 in the demo page. Choose d1 or an explicit no-AI heuristic comparison.\n2. Start game. Watch candidate metrics, the chosen drop, distributions and timing.\n3. Start audio separately. A pending music pattern changes at the next bar.\n4. Pause/Reset cancels pending decisions and rejects old results; errors pause rather than falling back. No camera, microphone, cloud or generated code. Comfy Run does not start game/audio.')
a=g.node('GeneretiCoreDecisionArcade','open Blocks & Beats',(0,370),(620,180))
g.lesson([('Open the arcade','Click ▦. The demo opens locally and stays idle until Start game.',a,'node'),('Follow a move','In the demo page, compare A–D candidates and the JSON decision. These options are legal placements, not raw keypresses.',a,'node'),('Conduct the soundtrack','Start audio explicitly. Compare current and next music patterns; changes land on bar boundaries.',a,'node'),('Compare decision strategies','Reset to seed 7 and select the heuristic player for a no-model baseline. Compare holes, height and cleared rows; d1 is not promised to win.',a,'node')]);g.save('08 - Blocks and Beats - decision arcade.json')
print('Built nine beginner samples')
