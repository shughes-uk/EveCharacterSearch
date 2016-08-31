var skillList = []
var npccorpList = []
var shipList = []
var filter_n = 1
var initialized = false
var corps_loaded = false
var skills_loaded = false
var ships_loaded = false
$(document).ready(function() {
  $("#thread_table").tablesorter({
    sortList: [
      [0, 0],
      [3, 1]
    ]
  });
});
$.ajax({
  type: 'GET',
  url: "/skills.json",
  dataType: 'json',
  success: function(data) {
    skillList = data;
    if (!initialized && corps_loaded && ships_loaded) {
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
    if (!initialized && skills_loaded && ships_loaded) {
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
    if (!initialized && skills_loaded && corps_loaded) {
      initialized = true
      start()
    }
    ships_loaded = true
  },
  async: true
});

function createSelect() {
  var select = document.createElement('select')
  select.className = 'styled-select col-md-2'
  return select
}

function delself() {
  parentNode.parentNode.removeChild(parentNode)
}

function start() {
  if (window.js_filters) {
    for (var i = 0; i < window.js_filters.length; i++) {
      var opBox = makeOperandsBox(filter_n, window.js_filters[i].operandSelect)
      var rowDiv = document.createElement('div')
      rowDiv.className = 'row filter'

      rowDiv.setAttribute('filter_number', filter_n)
      if (window.js_filters[i].filterType == 'sp') {
        filterType = makeFilterTypeSelect('sp')
        spBox = makeSPBox(filter_n, window.js_filters[i].sp_million)
        rowDiv.appendChild(filterType)
        rowDiv.appendChild(opBox)
        rowDiv.appendChild(spBox)
      } else if (window.js_filters[i].filterType == 'skill') {
        filterType = makeFilterTypeSelect('skill')
        catBox = makeSkillCatBox(filter_n, window.js_filters[i].groupID)
        skillBox = makeSkillBox(filter_n, window.js_filters[i].groupID, window.js_filters[i].skill_typeID)
        levelBox = makeLevelBox(filter_n, parseInt(window.js_filters[i].level_box))
        rowDiv.appendChild(filterType)
        rowDiv.appendChild(catBox)
        rowDiv.appendChild(skillBox)
        rowDiv.appendChild(opBox)
        rowDiv.appendChild(levelBox)
      } else if (window.js_filters[i].filterType == 'standing') {
        filterType = makeFilterTypeSelect('standing')
        corpBox = makeCorpNameBox(filter_n, window.js_filters[i].corporation_box)
        standingValBox = makeStandingValBox(filter_n, parseFloat(window.js_filters[i].standing_amount))
        rowDiv.appendChild(filterType)
        rowDiv.appendChild(corpBox)
        rowDiv.appendChild(opBox)
        rowDiv.appendChild(standingValBox)
      } else if (window.js_filters[i].filterType == 'cname') {
        filterType = makeFilterTypeSelect('cname')
        opBox = makeStringOpBox(filter_n, window.js_filters[i].stringOpSelect)
        nameBox = makeStringInputBox(filter_n, window.js_filters[i].sinput)
        rowDiv.appendChild(filterType)
        rowDiv.appendChild(opBox)
        rowDiv.appendChild(nameBox)
      } else if (window.js_filters[i].filterType == 'ship') {
        filterType = makeFilterTypeSelect('ship')
        catBox = makeShipCatBox(filter_n, window.js_filters[i].groupID)
        shipBox = makeShipBox(filter_n, window.js_filters[i].groupID, window.js_filters[i].ship_itemID)
        rowDiv.appendChild(filterType)
        rowDiv.appendChild(catBox)
        rowDiv.appendChild(shipBox)
      }

      rowDiv.appendChild(makeDelButton())
      document.forms.filters.insertBefore(rowDiv, document.forms.filters.lastElementChild)
      filter_n++
    }
  }
}

function addFilter() {
  var delbutton = makeDelButton()
  var filterType = makeFilterTypeSelect('skill')
  var catBox = makeSkillCatBox(filter_n, '266')
  var opBox = makeOperandsBox(filter_n)
  var skillBox = makeSkillBox(filter_n, '266', '11584')
  var levelBox = makeLevelBox(filter_n)
  var rowDiv = document.createElement('div')
  rowDiv.className = 'row filter'
  rowDiv.setAttribute('filter_number', filter_n)
  rowDiv.appendChild(filterType, rowDiv.firstChild)
  rowDiv.appendChild(catBox, rowDiv.firstChild)
  rowDiv.appendChild(skillBox, rowDiv.firstChild)
  rowDiv.appendChild(opBox, rowDiv.firstChild)
  rowDiv.appendChild(levelBox, rowDiv.firstChild)
  rowDiv.appendChild(delbutton, rowDiv.firstChild)
  document.forms.filters.insertBefore(rowDiv, document.forms.filters.lastElementChild)
  filter_n++
}

function makeSkillCatBox(fNumber, selectedID) {
  var skillCatSelect = createSelect()
  skillCatSelect.name = 'ci' + fNumber
  skillCatSelect.setAttribute('onChange', 'onSkillCatChange(this)')
  var catList = new Array()
  for (var i = 0; i < skillList.length; i++) {
    if (catList.indexOf(skillList[i]['fields']['groupName']) != -1) {
      continue
    } else {
      catList.push(skillList[i]['fields']['groupName'])
      var catOption = document.createElement('option')
      catOption.value = skillList[i]['fields']['groupID']
      catOption.innerHTML = skillList[i]['fields']['groupName']
      skillCatSelect.options.add(catOption)
      if (selectedID == skillList[i]['fields']['groupID']) {
        catOption.selected = true
      }
    }
  }
  return skillCatSelect
}

function makeSPBox(fNumber, selected) {
  var spSelect = createSelect()
  spSelect.name = 'sp' + fNumber
  spSelect.setAttribute('filter_number', fNumber)
  for (var i = 1; i <= 200; i++) {
    var newOption = document.createElement('option')
    newOption.value = i
    newOption.innerHTML = i + 'M'
    spSelect.options.add(newOption)
    if (i == selected) {
      newOption.selected = true
    }
  }
  return spSelect
}

function makeDelButton() {
  var del = document.createElement('img')
  del.setAttribute('onclick',
    'parentNode.parentNode.parentNode.removeChild(parentNode.parentNode)')
  del.innerHTML = 'Remove Filter'
  del.src = CLEAR_BUTTON_URL
  del.className = 'clear'

  var col = document.createElement('div')
  col.className = 'col-md-1 delbutton'
  col.appendChild(del)

  return col
}

function makeShipBox(fNumber, groupID, selectedID) {
  var shipBox = document.createElement('select');
  shipBox.name = "sh" + fNumber;
  shipBox.setAttribute('filter_number', fNumber);
  for (var i = 0; i < shipList.length; i++) {
    if (shipList[i]['fields']['groupID'] == groupID) {
      var shipOption = document.createElement('option');
      shipOption.value = shipList[i]['fields']['itemID'];
      shipOption.innerHTML = shipList[i]['fields']['name'];
      shipBox.options.add(shipOption);
      if (shipList[i]['fields']['itemID'] == selectedID) {
        shipOption.selected = true;
      }
    }
  }
  return shipBox;
}

function makeFilterTypeSelect(selectedType) {
  var filterType = createSelect()
  filterType.name = 'ft' + filter_n
  filterType.setAttribute('num', filter_n)
  filterType.setAttribute('onChange', 'onFilterTypeChange(this)')
  var sp = document.createElement('option')
  sp.value = 'sp'
  sp.innerHTML = 'SP'
  filterType.appendChild(sp)
  var skill = document.createElement('option')
  skill.value = 'skill'
  skill.innerHTML = 'Skill'
  filterType.appendChild(skill)
  if (selectedType == 'skill') {
    skill.selected = true
  }
  var standing = document.createElement('option')
  standing.value = 'standing'
  standing.innerHTML = 'Standing'
  filterType.appendChild(standing)
  if (selectedType == 'standing') {
    standing.selected = true
  }
  var cname = document.createElement('option')
  cname.value = 'cname'
  cname.innerHTML = 'Character Name'
  filterType.appendChild(cname)
  if (selectedType == 'cname') {
    cname.selected = true
  }
  var ship = document.createElement('option');
  ship.value = 'ship';
  ship.innerHTML = 'Ship';
  filterType.appendChild(ship)
  if (selectedType == 'ship') {
    ship.selected = true;
  }
  return filterType
}

function makeShipCatBox(fNumber, selectedID) {
  var shipCatSelect = document.createElement('select');
  shipCatSelect.name = 'ci' + fNumber;
  shipCatSelect.setAttribute('onChange', 'onShipCatChange(this)');
  var catList = new Array();
  for (var i = 0; i < shipList.length; i++) {
    if (catList.indexOf(shipList[i]['fields']['groupName']) != -1) {
      continue;
    } else {
      catList.push(shipList[i]['fields']['groupName']);
      var catOption = document.createElement('option');
      catOption.value = shipList[i]['fields']['groupID'];
      catOption.innerHTML = shipList[i]['fields']['groupName'];
      shipCatSelect.options.add(catOption);
      if (selectedID == shipList[i]['fields']['groupID']) {
        catOption.selected = true;
      }
    }
  }
  return shipCatSelect;
}

function makeOperandsBox(fNumber, selectedType) {
  var operandSelect = createSelect()
  operandSelect.name = 'op' + fNumber
  operandSelect.setAttribute('filter_number', fNumber)
  var geEq = document.createElement('option')
  geEq.value = 'ge'
  geEq.innerHTML = 'Greater than or equal to'
  var leEq = document.createElement('option')
  leEq.value = 'le'
  leEq.innerHTML = 'Less than or equal to'
  var eq = document.createElement('option')
  eq.value = 'eq'
  eq.innerHTML = 'Exactly'
  operandSelect.appendChild(geEq)
  operandSelect.appendChild(leEq)
  operandSelect.appendChild(eq)
  if (selectedType == 'ge') {
    geEq.selected = true
  }
  if (selectedType == 'le') {
    leEq.selected = true
  }
  if (selectedType == 'eq') {
    eq.selected = true
  }
  return operandSelect
}

function onFilterTypeChange(ele) {
  filterDiv = ele.parentNode
  while (filterDiv.firstChild) {
    if (filterDiv.childNodes.length > 1) {
      if (filterDiv.firstChild != ele) {
        filterDiv.removeChild(filterDiv.firstChild)
      } else {
        filterDiv.removeChild(filterDiv.lastChild)
      }
    } else {
      break
    }
  }
  selectedType = ele.options[ele.selectedIndex].value
  if (selectedType == 'sp') {
    spBox = makeSPBox(filterDiv.getAttribute('filter_number'))
    operandBox = makeOperandsBox(filterDiv.getAttribute('filter_number'))
    filterDiv.appendChild(operandBox)
    filterDiv.appendChild(spBox)
  } else if (selectedType == 'skill') {
    skillCatBox = makeSkillCatBox(filterDiv.getAttribute('filter_number'))
    filterDiv.appendChild(skillCatBox)
    onSkillCatChange(skillCatBox)
  } else if (selectedType == 'standing') {
    corpNameBox = makeCorpNameBox(filterDiv.getAttribute('filter_number'))
    standingValBox = makeStandingValBox(filterDiv.getAttribute('filter_number'))
    operandBox = makeOperandsBox(filterDiv.getAttribute('filter_number'))
    filterDiv.appendChild(corpNameBox)
    filterDiv.appendChild(operandBox)
    filterDiv.appendChild(standingValBox)
  } else if (selectedType == 'cname') {
    stringOpBox = makeStringOpBox(filterDiv.getAttribute('filter_number'))
    stringInput = makeStringInputBox(filterDiv.getAttribute('filter_number'))
    filterDiv.appendChild(stringOpBox)
    filterDiv.appendChild(stringInput)
  } else if (selectedType == 'ship') {
    shipCatBox = makeShipCatBox(filterDiv.getAttribute('filter_number'))
    filterDiv.appendChild(shipCatBox)
    onShipCatChange(shipCatBox)
  }
}

function makeStringOpBox(fNumber, selectedOp) {
  var operandSelect = createSelect()
  operandSelect.name = 'so' + fNumber
  operandSelect.setAttribute('filter_number', fNumber)
  var exact = document.createElement('option')
  exact.value = 'eq'
  exact.innerHTML = 'Exactly'
  var contains = document.createElement('option')
  contains.value = 'cnt'
  contains.innerHTML = 'Contains'
  operandSelect.appendChild(exact)
  operandSelect.appendChild(contains)
  if (selectedOp == 'eq') {
    exact.selected = true
  }
  if (selectedOp == 'cnt') {
    contains.selected = true
  }
  return operandSelect
}

function makeStringInputBox(fNumber, prefilled_string) {
  var inputBox = document.createElement('input')
  inputBox.name = 'si' + fNumber
  inputBox.setAttribute('filter_number', fNumber)
  if (typeof(prefilled_string) != 'undefined') {
    inputBox.value = prefilled_string
  }
  inputBox.className = 'col-md-2 styled-input'
  return inputBox
}

function makeCorpNameBox(fNumber, selectedCorp) {
  var corpBox = createSelect()
  corpBox.name = 'cb' + fNumber
  corpBox.setAttribute('filter_number', fNumber)
  for (var i = 0; i < npccorpList.length; i++) {
    var corpOption = document.createElement('option')
    corpOption.value = npccorpList[i]['fields']['name']
    corpOption.innerHTML = npccorpList[i]['fields']['name']
    if (npccorpList[i]['fields']['name'] == '-Security Status-') {
      corpBox.options.add(corpOption, corpBox.options.firstChild)
    } else {
      corpBox.options.add(corpOption)
    }
    if (npccorpList[i]['fields']['name'] == selectedCorp) {
      corpOption.selected = true
    }
  }
  return corpBox
}

function makeStandingValBox(fNumber, selected) {
  if (typeof(selected) == 'undefined') {
    selected = 0.0
  }
  var standingValBox = createSelect()
  standingValBox.name = 'sa' + fNumber
  standingValBox.setAttribute('filter_number', fNumber)
  for (var i = -10.0; i <= 10.0; i += 0.1) {
    i = parseFloat(i.toPrecision(4))
    var opt = document.createElement('option')
    opt.value = i
    opt.innerHTML = i
    standingValBox.appendChild(opt)
    if (i == selected) {
      opt.selected = true
    }
  }
  return standingValBox
}

function makeSkillBox(fNumber, groupID, selectedID) {
  var skillBox = createSelect()
  skillBox.name = 'ti' + fNumber
  skillBox.setAttribute('filter_number', fNumber)
  for (var i = 0; i < skillList.length; i++) {
    if (skillList[i]['fields']['groupID'] == groupID) {
      var skillOption = document.createElement('option')
      skillOption.value = skillList[i]['fields']['typeID']
      skillOption.innerHTML = skillList[i]['fields']['name']
      skillBox.options.add(skillOption)
      if (skillList[i]['fields']['typeID'] == selectedID) {
        skillOption.selected = true
      }
    }
  }
  return skillBox
}

function makeLevelBox(fNumber, selected) {
  var levelBox = createSelect()
  levelBox.name = 'lb' + fNumber
  levelBox.setAttribute('filter_number', fNumber)
  var one = document.createElement('option')
  one.value = '1'
  one.innerHTML = 'I'
  levelBox.appendChild(one)
  var two = document.createElement('option')
  two.value = '2'
  two.innerHTML = 'II'
  levelBox.appendChild(two)
  var three = document.createElement('option')
  three.value = '3'
  three.innerHTML = 'III'
  levelBox.appendChild(three)
  var four = document.createElement('option')
  four.value = '4'
  four.innerHTML = 'IV'
  levelBox.appendChild(four)
  var five = document.createElement('option')
  five.value = '5'
  five.innerHTML = 'V'
  levelBox.appendChild(five)
  switch (selected) {
    case 1:
      one.selected = true
      break
    case 2:
      two.selected = true
      break
    case 3:
      three.selected = true
      break
    case 4:
      four.selected = true
      break
    case 5:
      five.selected = true
      break
    default:
      break
  }
  return levelBox
}

function onSkillCatChange(ele) {
  var fNumber = ele.parentNode.getAttribute('filter_number')
  var groupID = ele.options[ele.selectedIndex].value
  while (ele.parentNode.lastChild) {
    if (ele.parentNode.lastChild != ele) {
      ele.parentNode.removeChild(ele.parentNode.lastChild)
    } else {
      break
    }
  }
  ele.parentNode.appendChild(makeSkillBox(fNumber, groupID))
  ele.parentNode.appendChild(makeOperandsBox(fNumber))
  ele.parentNode.appendChild(makeLevelBox(fNumber))
}

function onShipCatChange(ele) {
  var fNumber = ele.parentNode.getAttribute('filter_number');
  var groupID = ele.options[ele.selectedIndex].value;
  while (ele.parentNode.lastChild) {
    if (ele.parentNode.lastChild != ele) {
      ele.parentNode.removeChild(ele.parentNode.lastChild);
    } else {
      break
    }
  }
  ele.parentNode.appendChild(makeShipBox(fNumber, groupID));
}
