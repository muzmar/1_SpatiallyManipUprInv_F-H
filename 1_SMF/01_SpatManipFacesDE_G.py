# -*- coding: utf-8 -*-
'''
@author: Florian Niefind
@contact: nifflor@googlemail.com
@date: 2014-05-21
'''

# TO do: will there be chinese pictures? yes!

from psychopy import visual, core, event, gui, data
from random import shuffle
import string, codecs


# ===============================================================================
# global variables: INTERFACE
# ===============================================================================

# PATH = 'D:/Tests/____TASKs_FACEProject/___Reprogramming/vonFlorian/vonFlorian/FaceRecognitionBattery_Andrea/01'
PATH = "C:/pythonProjects/1_SpatiallyManipUprInv_F&H/1_SMF"
FIXCROSS_SIZE = 40  # size of the fixation cross (the character '+' in Arial)
INSTR_CHAR_SIZE = 18  # character size for instructions
OUTPATH = '%s/results/'%(PATH)  # output path for storing the results
AVAILABLE_KEYS = ['lctrl', 'rctrl', 'q']
LANGUAGE = 'DE'  # which language is the experiment in: 'DE'=German. 'CN'=Chinese
MATCHING = {'lctrl':'different', 'rctrl':'same'} #matching of buttons to answers
SCREEN_SIZE = [1366, 768] #what is your screen resolution?
LANG_FONT_MAP = {'DE':'Courier New', 'CN':'SimSun'} #what font is used for what language?

# ===============================================================================
# prepare psychopy
# ===============================================================================

# gather experiment and subject information
exp_name = 'SpatiallyManipFaces'
exp_info = {'Subject':'', 'Subject (repeat)':''}

# prompt user for subject number
dlg = gui.DlgFromDict(dictionary=exp_info, title=exp_name)
if dlg.OK == False:
    core.quit()  # user pressed cancel

# if repetition and original do not match, repeat prompt
while exp_info['Subject'] != exp_info['Subject (repeat)']:
    dlg = gui.DlgFromDict(dictionary=exp_info, title='Please insert matching number in both fields')
    if dlg.OK == False:
        core.quit()  # user pressed cancel

# dictionary with additional info about the experiment
exp_info['date'] = data.getDateStr()#add a simple timestamp
exp_info['exp_name'] = exp_name

# create a window
exp_win = visual.Window(size=SCREEN_SIZE, monitor="testMonitor", color=(230,230,230), fullscr=True,
                        colorSpace='rgb255', units="deg")

# ===============================================================================
# read stimuli
# ===============================================================================


def read_stims(stim_file):
    item_list = []
    trial_order = []  # order of the trials in the experiment (hard-coded in the trial file)
    with codecs.open(stim_file, 'rb', encoding="utf-8") as infile:
        for line in infile:
            line = line.strip()
            if '###' in line:  # its the header
                continue
            elif len(line) == 0:  # last line if an empty one
                break
            line = line.split(';')
            trial_order.append(int(line[9]))  # trial order
            item_list.append(line[0:9])  # write entire rest of the line
    return item_list, trial_order

practice_items, practice_trial_order = read_stims('%s/%s/stimuli/Practice_SpatManipFaces_%s.txt'%(PATH,LANGUAGE,LANGUAGE))
items, trial_order = read_stims('%s/%s/stimuli/Trials_SpatManipFaces_%s.txt'%(PATH,LANGUAGE,LANGUAGE))

# ===============================================================================
# Other preparations
# ===============================================================================

# width for text wrapping
wrap_width = SCREEN_SIZE[0]-100
font = LANG_FONT_MAP[LANGUAGE]  # font based on language selection

output_file = OUTPATH + exp_info['exp_name'] + '_%02i.txt'%(int(exp_info['Subject']))
rt_clock = core.Clock()  # reaction time clock

# fixation cross
fix_cross = visual.TextStim(exp_win, pos=[0, 0], text = '+', font='Arial', color=-1,
                            height=FIXCROSS_SIZE, alignHoriz='center', units=u'pix')

# ------------------------------------------------------------------------------
# read instructions
# NOTE: It was decided that we use images for instructions so they are easy to change. To present those
#   we use SimpleImageStim because these are not internally rescaled and thus interpolated. This would 
#   make the text look very ugly. SimpleImageStims draw more slowly and need to be in the final size 
#   upon creation (1024*768).
#   Time critical screens which require quick drawing are done as TextStims or ImageStims.

try:
    instr_screen = visual.SimpleImageStim(exp_win, image='%s/%s/Instruction_Screen_%s.png'%(PATH, LANGUAGE, LANGUAGE))
    practice_start_screen = visual.SimpleImageStim(exp_win, image='%s/%s/Practice_Start_Screen_%s.png'%(PATH, LANGUAGE, LANGUAGE))
    practice_end_screen = visual.SimpleImageStim(exp_win, image='%s/%s/Practice_End_Screen_%s.png'%(PATH, LANGUAGE, LANGUAGE))
    test_end_screen = visual.SimpleImageStim(exp_win, image='%s/%s/Test_End_Screen_%s.png'%(PATH, LANGUAGE, LANGUAGE))
    with codecs.open('%s/%s/Reminder_%s.txt'%(PATH,LANGUAGE,LANGUAGE), 'rb', encoding='utf-8') as infile:
        rem_text = infile.read()
    with codecs.open('%s/%s/Correct_Screen_%s.txt'%(PATH,LANGUAGE,LANGUAGE), 'rb', encoding='utf-8') as infile:
        correct_text = infile.read()
    with codecs.open('%s/%s/Incorrect_Screen_%s.txt'%(PATH,LANGUAGE,LANGUAGE), 'rb', encoding='utf-8') as infile:
        incorrect_text = infile.read()
except IOError:
    print 'Error: Language option set to unknown language. Choose DE for German or CN for Chinese.'
    exp_win.close()
    core.quit()

# answer possibilities shown
reminder_screen = visual.TextStim(exp_win, pos=[0, -300], text=rem_text, font=font, color=-1,
                                  height=INSTR_CHAR_SIZE, alignHoriz='center', wrapWidth=wrap_width, units=u'pix')

# feedback screens practice
correct_screen = visual.TextStim(exp_win, pos=[0, 0], text=correct_text, font=font, color=(-1, 1.0, -1),
                                 height=40, alignHoriz='center', wrapWidth=wrap_width, units=u'pix')
incorrect_screen = visual.TextStim(exp_win, pos=[0, 0], text=incorrect_text, font=font, color=(1.0, -1, -1),
                                   height=40, alignHoriz='center', wrapWidth=wrap_width, units=u'pix')

def match_answer(answer_given, condition):
    '''
    Function to match the answer of the participant with the correct answer.
    lctrl: different
    rctrl: same
    '''
    return int(MATCHING.get(answer_given, 'escape') == condition)

# ------------------------------------------------------------------------------
# define trial procedure


def run_trials(items, trial_order, practice=False):
    
    # ## NOTE: If one wants a random order each time, uncomment the following two lines
    # trial_order = range(len(items)) #NOTE: initial seed is system time, so it is different each time
    # shuffle(trial_order)
    
    if practice:
        item_prefix = 'psmsmf'
    else:
        item_prefix = 'smsmf'
    
    trial_count = 1
    
    # loop through trials
    for i in trial_order:
        
        item = items[i-1]
        
        # prepare stimulus and draw on screen
        stim_left = visual.ImageStim(exp_win, image='%s/%s/stimuli/%s%s'%(PATH, LANGUAGE, item_prefix,
                                                                          item[7]), pos=[-200,0], units=u'pix')
        stim_right = visual.ImageStim(exp_win, image='%s/%s/stimuli/%s%s'%(PATH, LANGUAGE, item_prefix,
                                                                           item[8]), pos=[200,0], units=u'pix')
        
        # pre-stimulus interval
        exp_win.flip()  # flip blank screen
        core.wait(1.3)  # 1300 ms
        
        # fix_cross
        fix_cross.draw()
        exp_win.flip()
        core.wait(0.2) # 200 ms
        # blank (1 cycle)
        exp_win.flip()
        
        # draw to back buffer
        stim_left.draw()
        stim_right.draw()
        reminder_screen.draw()
        # present
        exp_win.flip()
        
        # start reaction time clock and collect answer
        rt_clock.reset()
        ans = event.waitKeys(keyList=AVAILABLE_KEYS)
        
        # get reaction time
        rt = rt_clock.getTime()
        
        # write out answers
        string_output = [exp_info['Subject'], str(trial_count)]  # initialize output list: subject ID, trial number (in exp)
        string_output.extend([str(x) for x in item])  # add trial infos
        string_output.extend([str(int(practice)),str(ans[-1]), str(match_answer(ans[-1], item[6])), str(rt)])  # add answer infos
        outfile.write(';'.join(string_output) + '\n')  # write to file
        
        if practice and match_answer(ans[-1], item[6]):
            correct_screen.draw()
            exp_win.flip()
            core.wait(1)
        elif practice:
            incorrect_screen.draw()
            exp_win.flip()
            core.wait(1)
        
        # check if experiment was aborted
        if len(ans) == 2:
            if ans[-2] == 'lctrl' and ans[-1] == 'q':
                exp_win.close()
                core.quit()

        # check for quit
        if ans[-1] == "q":
            core.quit()
        
        trial_count += 1

# ===============================================================================
# experiment
# ===============================================================================

# ------------------------------------------------------------------------------
# present instructions
instr_screen.draw()
exp_win.flip()
event.waitKeys(keyList=['space'])

# ------------------------------------------------------------------------------
# run experiment
with codecs.open(output_file, 'wb', encoding="utf-8") as outfile:
    
    # write outfile header
    # outfile.write('### Experiment: %s\n### Subject ID: %s\n### Date: %s\n\n' %(exp_info['exp_name'], exp_info['Subject'], exp_info['date']))
    outfile.write('subject_id;trial;trial_id;vert_orientation;face_id;sex;spat_chng;chngd_face_pos;cond;image_name_l;image_name_r;practice;ans;correct;rt\n') #header
    
    # practice start if no questions
    practice_start_screen.draw()
    exp_win.flip()
    event.waitKeys(keyList=['space'])
    
    # run practice trials
    run_trials(practice_items, practice_trial_order, practice=True)
    
    # practice end
    practice_end_screen.draw()
    exp_win.flip()
    event.waitKeys(keyList=['space'])
    
    # exp start
    run_trials(items, trial_order)

test_end_screen.draw()
exp_win.flip()
event.waitKeys()

exp_win.close()
core.quit()
