var skillList = []
var npccorpList = []
var shipList = []
var filter_n = 1
var initialized = false
var corps_loaded = false
var skills_loaded = false
var ships_loaded = false
$(document).ready(function(){
    $("#thread_table").tablesorter({
        sortList:[[0,0],[3,1]]
    });
}
);
$.ajax({
      type: 'GET',
      url: "/skills.json",
      dataType: 'json',
      success: function(data) {
            skillList = data;
            if (!initialized  && corps_loaded && ships_loaded)
            {
                initialized = true
                start()
            }
            skills_loaded = true
        },
      async: true
    });
$.ajax({
      type: 'GET',
      url: "/npc_corps.json",
      dataType: 'json',
      success: function(data) {
          npccorpList = data;
          if (!initialized  && skills_loaded && ships_loaded)
          {
              initialized = true
              start()
          }
          corps_loaded = true
      },
      async: true
    });
$.ajax({
      type: 'GET',
      url: "/ships.json",
      dataType: 'json',
      success: function(data) {
          shipList = data;
          if (!initialized  && skills_loaded && corps_loaded)
          {
              initialized = true
              start()
          }
          ships_loaded = true
      },
      async: true
    });


function delself(){
    parentNode.parentNode.removeChild(parentNode)
}

function start() {
    if (window.js_filters)
    {
        for (var i = 0; i < window.js_filters.length; i++)
        {
            delbutton = makeDelButton()
            opBox = makeOperandsBox(filter_n,window.js_filters[i].operandSelect)
            var optionsDiv = document.createElement('span')
            optionsDiv.setAttribute('filter_number',filter_n)
            var mainDiv = document.createElement('div')
            if (window.js_filters[i].filterType == "sp")
            {
                filterType = makeFilterTypeSelect('sp')
                spBox = makeSPBox(filter_n,window.js_filters[i].sp_million)
                optionsDiv.appendChild(filterType)
                optionsDiv.appendChild(opBox)
                optionsDiv.appendChild(spBox)
            }
            else if(window.js_filters[i].filterType == "skill")
            {
                filterType = makeFilterTypeSelect('skill')
                catBox = makeSkillCatBox(filter_n,window.js_filters[i].groupID)
                skillBox = makeSkillBox(filter_n,window.js_filters[i].groupID,window.js_filters[i].skill_typeID)
                levelBox = makeLevelBox(filter_n,parseInt(window.js_filters[i].level_box))
                optionsDiv.appendChild(filterType)
                optionsDiv.appendChild(catBox)
                optionsDiv.appendChild(skillBox)
                optionsDiv.appendChild(opBox)
                optionsDiv.appendChild(levelBox)
            }
            else if(window.js_filters[i].filterType == "standing")
            {
                filterType = makeFilterTypeSelect('standing');
                corpBox = makeCorpNameBox(filter_n,window.js_filters[i].corporation_box);
                standingValBox = makeStandingValBox(filter_n,parseFloat(window.js_filters[i].standing_amount));
                optionsDiv.appendChild(filterType);
                optionsDiv.appendChild(corpBox);
                optionsDiv.appendChild(opBox);
                optionsDiv.appendChild(standingValBox);
            }
            else if(window.js_filters[i].filterType == "cname")
            {
                filterType = makeFilterTypeSelect('cname')
                opBox = makeStringOpBox(filter_n,window.js_filters[i].stringOpSelect)
                nameBox = makeStringInputBox(filter_n,window.js_filters[i].sinput)
                optionsDiv.appendChild(filterType)
                optionsDiv.appendChild(opBox)
                optionsDiv.appendChild(nameBox)
            }
            else if(window.js_filters[i].filterType == "ship")
            {
                filterType = makeFilterTypeSelect('ship')
                catBox = makeShipCatBox(filter_n,window.js_filters[i].groupID)
                shipBox = makeShipBox(filter_n,window.js_filters[i].groupID,window.js_filters[i].ship_itemID)
                optionsDiv.appendChild(filterType)
                optionsDiv.appendChild(catBox)
                optionsDiv.appendChild(shipBox)
            }
            mainDiv.insertBefore(document.createElement('br'),mainDiv.firstChild);
            mainDiv.insertBefore(delbutton,mainDiv.firstChild);
            mainDiv.insertBefore(optionsDiv,mainDiv.firstChild)
            document.forms.filters.insertBefore(mainDiv,document.forms.filters.lastElementChild);
            if (filter_n % 2 == 1)
            {
                mainDiv.setAttribute('class','div_odd')
            }
            else
            {
                mainDiv.setAttribute('class','div_even')
            }
            filter_n++
        }
    }
}
function addFilter() {
    delbutton = makeDelButton()
    filterType = makeFilterTypeSelect('skill')
    catBox = makeSkillCatBox(filter_n,'266')
    opBox = makeOperandsBox(filter_n)
    skillBox = makeSkillBox(filter_n,'266','11584')
    levelBox = makeLevelBox(filter_n)
    var optionsDiv = document.createElement('span')
    optionsDiv.appendChild(filterType,optionsDiv.firstChild);
    optionsDiv.appendChild(catBox,optionsDiv.firstChild);
    optionsDiv.appendChild(skillBox,optionsDiv.firstChild);
    optionsDiv.appendChild(opBox,optionsDiv.firstChild);
    optionsDiv.appendChild(levelBox,optionsDiv.firstChild);
    optionsDiv.setAttribute('filter_number',filter_n)
    var div = document.createElement('div');
    div.insertBefore(document.createElement('br'),div.firstChild);
    div.insertBefore(delbutton,div.firstChild);
    div.insertBefore(optionsDiv,div.firstChild)
    document.forms.filters.insertBefore(div,document.forms.filters.lastElementChild);
    if (filter_n % 2 == 1)
    {
        div.setAttribute('class','div_odd')
    }
    else
    {
        div.setAttribute('class','div_even')
    }
    filter_n++;
}
function makeSkillCatBox(fNumber,selectedID){
    var skillCatSelect = document.createElement('select');
    skillCatSelect.name = "ci" + fNumber;
    skillCatSelect.setAttribute('onChange','onSkillCatChange(this)');
    var catList = new Array();
    for (var i = 0; i < skillList.length; i++)
    {
        if (catList.indexOf(skillList[i]['fields']['groupName']) != -1)
        {
            continue;
        }
        else
        {
            catList.push(skillList[i]['fields']['groupName']);
            var catOption = document.createElement('option');
            catOption.value = skillList[i]['fields']['groupID'];
            catOption.innerHTML = skillList[i]['fields']['groupName'];
            skillCatSelect.options.add(catOption);
            if (selectedID == skillList[i]['fields']['groupID'])
            {
                catOption.selected = true;

            }
        }
    }
    return skillCatSelect;
}
function makeSPBox(fNumber,selected){
    var spSelect = document.createElement('select');
    spSelect.name = "sp" + fNumber;
    spSelect.setAttribute('filter_number',fNumber)
    for(var i=1;i<=200;i++)
    {
        var newOption = document.createElement('option');
        newOption.value = i;
        newOption.innerHTML= i +'M';
        spSelect.options.add(newOption);
        if (i == selected)
        {
            newOption.selected = true;
        }
    }
    return spSelect
}
function makeDelButton(){
    var delbutton = document.createElement('img');
    delbutton.setAttribute('onclick','parentNode.parentNode.removeChild(parentNode)');
    delbutton.innerHTML = 'Remove Filter';
    delbutton.src = CLEAR_BUTTON_URL
    delbutton.className = "clear"
    return delbutton
}

function makeFilterTypeSelect(selectedType){
    var filterType = document.createElement('select');
    filterType.name = 'ft' + filter_n;
    filterType.setAttribute('num', filter_n);
    filterType.setAttribute('onChange','onFilterTypeChange(this)');
    var sp = document.createElement('option');
    sp.value = 'sp';
    sp.innerHTML = 'SP';
    filterType.appendChild(sp)
    var skill = document.createElement('option');
    skill.value = 'skill';
    skill.innerHTML = 'Skill'
    filterType.appendChild(skill)
    if (selectedType == 'skill')
    {
        skill.selected = true;
    }
    var standing = document.createElement('option');
    standing.value = 'standing';
    standing.innerHTML = 'Standing';
    filterType.appendChild(standing)
    if (selectedType == 'standing')
    {
        standing.selected = true;
    }
    var cname = document.createElement('option');
    cname.value = 'cname';
    cname.innerHTML = 'Character Name';
    filterType.appendChild(cname)
    if (selectedType == 'cname')
    {
        cname.selected = true;
    }
    var ship = document.createElement('option');
    ship.value = 'ship';
    ship.innerHTML = 'Ship';
    filterType.appendChild(ship)
    if (selectedType == 'ship')
    {
        ship.selected = true;
    }
    return filterType;
}
function makeOperandsBox(fNumber,selectedType){
    var operandSelect = document.createElement('select');
    operandSelect.name = "op" + fNumber;
    operandSelect.setAttribute('filter_number',fNumber);
    var geEq = document.createElement('option');
    geEq.value = 'ge';
    geEq.innerHTML = 'Greater than or equal to';
    var leEq = document.createElement('option');
    leEq.value = 'le';
    leEq.innerHTML = 'Less than or equal to';
    var eq = document.createElement('option');
    eq.value = 'eq';
    eq.innerHTML = 'Exactly';
    operandSelect.appendChild(geEq);
    operandSelect.appendChild(leEq);
    operandSelect.appendChild(eq);
    if (selectedType =='ge')
    {
        geEq.selected = true
    }
    if (selectedType == 'le')
    {
        leEq.selected = true
    }
    if (selectedType == 'eq')
    {
        eq.selected = true
    }
    return operandSelect;
}
function onFilterTypeChange(ele){
    filterDiv = ele.parentNode;
    while (filterDiv.firstChild)
    {
        if (filterDiv.childNodes.length > 1)
        {
            if (filterDiv.firstChild != ele)
            {
                filterDiv.removeChild(filterDiv.firstChild)
            }
            else
            {
                filterDiv.removeChild(filterDiv.lastChild)
            }
        }
        else
        {
            break
        }
    }
    selectedType = ele.options[ele.selectedIndex].value;
    if (selectedType == 'sp')
    {
        spBox = makeSPBox(filterDiv.getAttribute('filter_number'));
        operandBox = makeOperandsBox(filterDiv.getAttribute('filter_number'));
        filterDiv.appendChild(operandBox);
        filterDiv.appendChild(spBox);

    }
    else if (selectedType == 'skill')
    {
        skillCatBox = makeSkillCatBox(filterDiv.getAttribute('filter_number'));
        filterDiv.appendChild(skillCatBox);
        onSkillCatChange(skillCatBox);
    }
    else if (selectedType == 'standing')
    {
        corpNameBox = makeCorpNameBox(filterDiv.getAttribute('filter_number'));
        standingValBox = makeStandingValBox(filterDiv.getAttribute('filter_number'));
        operandBox = makeOperandsBox(filterDiv.getAttribute('filter_number'));
        filterDiv.appendChild(corpNameBox);
        filterDiv.appendChild(operandBox);
        filterDiv.appendChild(standingValBox);
    }
    else if (selectedType == 'cname')
    {
        stringOpBox = makeStringOpBox(filterDiv.getAttribute('filter_number'))
        stringInput = makeStringInputBox(filterDiv.getAttribute('filter_number'))
        filterDiv.appendChild(stringOpBox)
        filterDiv.appendChild(stringInput)
    }
    else if (selectedType == 'ship')
    {
        shipCatBox = makeShipCatBox(filterDiv.getAttribute('filter_number'))
        filterDiv.appendChild(shipCatBox)
        onShipCatChange(shipCatBox)
    }
}
function makeShipBox(fNumber , groupID , selectedID){
    var shipBox = document.createElement('select');
    shipBox.name = "sh" + fNumber;
    shipBox.setAttribute('filter_number' , fNumber);
    for (var i = 0; i < shipList.length; i++)
    {
        if (shipList[i]['fields']['groupID'] == groupID)
        {
            var shipOption = document.createElement('option');
            shipOption.value = shipList[i]['fields']['itemID'];
            shipOption.innerHTML = shipList[i]['fields']['name'];
            shipBox.options.add(shipOption);
            if (shipList[i]['fields']['itemID'] == selectedID)
            {
                shipOption.selected  = true;
            }
        }
    }
    return shipBox;
}
function makeShipCatBox(fNumber,selectedID)
{
    var shipCatSelect = document.createElement('select');
    shipCatSelect.name = "ci" + fNumber;
    shipCatSelect.setAttribute('onChange','onShipCatChange(this)');
    var catList = new Array();
    for (var i = 0; i < shipList.length; i++)
    {
        if (catList.indexOf(shipList[i]['fields']['groupName']) != -1)
        {
            continue;
        }
        else
        {
            catList.push(shipList[i]['fields']['groupName']);
            var catOption = document.createElement('option');
            catOption.value = shipList[i]['fields']['groupID'];
            catOption.innerHTML = shipList[i]['fields']['groupName'];
            shipCatSelect.options.add(catOption);
            if (selectedID == shipList[i]['fields']['groupID'])
            {
                catOption.selected = true;

            }
        }
    }
    return shipCatSelect;
}
function makeStringOpBox(fNumber , selectedOp){
    var operandSelect = document.createElement('select');
    operandSelect.name = "so" + fNumber;
    operandSelect.setAttribute('filter_number',fNumber);
    var exact = document.createElement('option');
    exact.value = 'eq';
    exact.innerHTML = 'Exactly';
    var contains = document.createElement('option');
    contains.value = 'cnt';
    contains.innerHTML = 'Contains';

    operandSelect.appendChild(exact);
    operandSelect.appendChild(contains);
    if (selectedOp == 'eq')
    {
        exact.selected = true
    }
    if (selectedOp == 'cnt')
    {
        contains.selected = true
    }
    return operandSelect;

}

function makeStringInputBox(fNumber , prefilled_string){
    var inputBox = document.createElement('input');
    inputBox.name = "si" + fNumber;
    inputBox.setAttribute('filter_number',fNumber);
    if (typeof(prefilled_string) != 'undefined'){
        inputBox.value = prefilled_string
    }
    return inputBox
}

function makeCorpNameBox(fNumber  , selectedCorp){
    var corpBox = document.createElement('select');
    corpBox.name = "cb" + fNumber;
    corpBox.setAttribute('filter_number' , fNumber);
    for (var i = 0; i < npccorpList.length; i++)
    {
        var corpOption = document.createElement('option');
        corpOption.value = npccorpList[i]['fields']['name'];
        corpOption.innerHTML = npccorpList[i]['fields']['name'];
        if (npccorpList[i]['fields']['name'] == '-Security Status-')
        {
            corpBox.options.add(corpOption,corpBox.options.firstChild);
        }
        else
        {
            corpBox.options.add(corpOption);
        }
        if (npccorpList[i]['fields']['name'] == selectedCorp)
        {
            corpOption.selected  = true;
        }
    }
    return corpBox;
}

function makeStandingValBox(fNumber , selected){
    if (typeof(selected) == "undefined")
    {
        selected = 0.0
    }
    var standingValBox = document.createElement('select');
    standingValBox.name = "sa" + fNumber;
    standingValBox.setAttribute('filter_number',fNumber);
    for (var i = -10.0; i <= 10.0;i += 0.1)
    {
        i = parseFloat(i.toPrecision(4))
        var opt = document.createElement('option');
        opt.value = i;
        opt.innerHTML = i;
        standingValBox.appendChild(opt);
        if (i == selected)
        {
            opt.selected = true;
        }
    }
    return standingValBox
}

function makeSkillBox(fNumber , groupID , selectedID){
    var skillBox = document.createElement('select');
    skillBox.name = "ti" + fNumber;
    skillBox.setAttribute('filter_number' , fNumber);
    for (var i = 0; i < skillList.length; i++)
    {
        if (skillList[i]['fields']['groupID'] == groupID)
        {
            var skillOption = document.createElement('option');
            skillOption.value = skillList[i]['fields']['typeID'];
            skillOption.innerHTML = skillList[i]['fields']['name'];
            skillBox.options.add(skillOption);
            if (skillList[i]['fields']['typeID'] == selectedID)
            {
                skillOption.selected  = true;
            }
        }
    }
    return skillBox;
}

function makeLevelBox(fNumber , selected){
    var levelBox = document.createElement('select');
    levelBox.name = "lb" + fNumber;
    levelBox.setAttribute('filter_number',fNumber);

    var one = document.createElement('option');
    one.value = '1';
    one.innerHTML = 'I';
    levelBox.appendChild(one)
    var two = document.createElement('option');
    two.value = '2';
    two.innerHTML = 'II';
    levelBox.appendChild(two);
    var three = document.createElement('option');
    three.value = '3';
    three.innerHTML = 'III';
    levelBox.appendChild(three);
    var four = document.createElement('option');
    four.value = '4';
    four.innerHTML = 'IV';
    levelBox.appendChild(four);
    var five = document.createElement('option');
    five.value = '5';
    five.innerHTML = 'V';
    levelBox.appendChild(five);
    switch(selected)
    {
        case 1:
            one.selected = true;
            break;
        case 2:
            two.selected = true;
            break;
        case 3:
            three.selected = true;
            break;
        case 4:
            four.selected = true;
            break;
        case 5:
            five.selected = true;
            break;
        default:
            break;
    }
    return levelBox
}

function onSkillCatChange(ele){
    var fNumber = ele.parentNode.getAttribute('filter_number');
    var groupID = ele.options[ele.selectedIndex].value;
    while (ele.parentNode.lastChild)
    {
        if (ele.parentNode.lastChild != ele)
        {
            ele.parentNode.removeChild(ele.parentNode.lastChild);
        }
        else
        {
            break
        }
    }
    ele.parentNode.appendChild(makeSkillBox(fNumber,groupID));
    ele.parentNode.appendChild(makeOperandsBox(fNumber));
    ele.parentNode.appendChild(makeLevelBox(fNumber));
}
function onShipCatChange(ele){
    var fNumber = ele.parentNode.getAttribute('filter_number');
    var groupID = ele.options[ele.selectedIndex].value;
    while (ele.parentNode.lastChild)
    {
        if (ele.parentNode.lastChild != ele)
        {
            ele.parentNode.removeChild(ele.parentNode.lastChild);
        }
        else
        {
            break
        }
    }
    ele.parentNode.appendChild(makeShipBox(fNumber,groupID));
}
