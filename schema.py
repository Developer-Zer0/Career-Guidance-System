import random

orig_schema = {
  'Demographics':
   {
    'Name': '',
    'Age': '',
    'Gender': '',
    'Race': '',
    'Current-Residence': '',
    'Previous-Residences': [''],
    },

  'Personality':
   {
    'Goals': [''],
    'Likes': [''],
    'Dislikes': [''],
    'Hobbies': [''],
    'Notes': [''],
    },

  'Relationships':
   {
    'Father':
    [
      {
        'Name': '',
        'Jobs': [''],
        'Notes': [''],
        },
     ],
    'Mother':
    [
      {
        'Name': '',
        'Jobs': [''],
        'Notes': [''],
        },
    ],
    'Siblings':
    [
         {
        'Name': '',
        'Relationship': '',
        'Jobs': [''],
        'Notes': [''],
        },
      ],
    },

  'Work-Experience':
   [
       {
        'Company name': '',
        'Role': '',
        'Length': '',
        'Description': '',
        },
    ],

  'Education':
   {
    'Elementary-School': [
       {
        'Institution-Name': '',
        'Length': '',
        'Description': '',
        }],
    'Middle-School': [
       {
        'Institution-Name': '',
        'Length': '',
        'Description': '',
        }],
    'High-School': [
       {
        'Institution-Name': '',
        'Length': '',
        'Description': '',
        }],
    'College': [
       {
        'Institution-Name': '',
        'Degree': '',
        'Length': '',
        'Description': '',
        }],
   },
}

schema_limit = {
  'Demographics':
   {
    'Name': (0, []),
    'Age': (0, []),
    'Gender': (0, []),
    'Race': (0, []),
    'Current-Residence': (0, []),
    'Previous-Residences': (3, [1, 0.5, 0.1]),
    },

  'Personality':
   {
    'Goals': (3, [1, 0.5, 0.1]),
    'Likes': (5, [1, 0.8, 0.6, 0.4, 0.2]),
    'Dislikes': (5, [1, 0.8, 0.6, 0.4, 0.2]),
    'Hobbies': (3, [1, 0.5, 0.1]),
    'Notes': (100, []),
    },

  'Relationships':
   {
    'Father': (1, []),
    'Mother': (1, []),
    'Siblings': (3, [1, 0.5, 0.1]),
    },

  'Work-Experience': (3, [1, 0.5, 0.1]),

  'Education':
   {
    'Elementary-School': (3, [1, 0.5, 0.1]),
    'Middle-School': (3, [1, 0.5, 0.1]),
    'High-School': (3, [1, 0.5, 0.1]),
    'College': (1, [0.5]),
   },
}

class Schema():

  def __init__(self, orig_schema, schema_limit):
    self.orig_schema = orig_schema
    self.curr_schema = orig_schema
    self.schema_limit = schema_limit

  def get_schema(self):
    return self.curr_schema

  # def update_all_elements(self):
  #   for key, value in self.orig_schema.items():
  #     if isinstance(self.orig_schema[key], dict):
  #     else:

  def get_field_new_element(self, field_string):
    # field_string example: Education_High-School
    prob = self.get_new_element_prob(field_string)
    print('New element of', field_string, 'with probability', prob)
    rand = random.uniform(0,1)
    if rand > prob:
      return False
    fs = field_string.split('_')
    hd = fs[0]
    if isinstance(self.orig_schema[hd], dict):
      assert len(fs) == 2
      if isinstance(self.orig_schema[hd][fs[1]], list):
        self.curr_schema[hd][fs[1]].append(self.orig_schema[hd][fs[1]][0])
        return True
      else:
        return False
    else:
      self.curr_schema[hd].append(self.orig_schema[hd][0])
      return True

  def get_new_element_prob(self, field_string):
    # field_string example: Education_High-School
    fs = field_string.split('_')
    hd = fs[0]
    if isinstance(self.orig_schema[hd], dict):
      assert len(fs) == 2
      lim = self.schema_limit[hd][fs[1]][0]
      # print(len(self.curr_schema[hd][fs[1]]), lim)
      if lim == 100:
        return 1
      prob_list = self.schema_limit[hd][fs[1]][1]
      if len(self.curr_schema[hd][fs[1]]) == lim:
        return 0
      else:
        return prob_list[len(self.curr_schema[hd][fs[1]])]
    else:
      lim = self.schema_limit[hd][0]
      prob_list = self.schema_limit[hd][1]
      if len(self.curr_schema[hd]) == lim:
        return 0
      else:
        return prob_list[len(self.curr_schema[hd])]

  def is_empty(self, field_string):
    fs = field_string.split('_')
    hd = fs[0]
    try:
      if isinstance(self.curr_schema[hd], dict):
        assert len(fs) == 2
        if isinstance(self.curr_schema[hd][fs[1]], list):
          # print(fs, self.curr_schema[hd][fs[1]], self.orig_schema[hd][fs[1]])
          # print(self.curr_schema[hd][fs[1]][-1] == self.orig_schema[hd][fs[1]][0])
          if self.curr_schema[hd][fs[1]][-1] == self.orig_schema[hd][fs[1]][0]:
            return True
          else:
            return False
        else:
          if self.curr_schema[hd][fs[1]] == '':
            return True
          else:
            return False
      else:
        if self.curr_schema[hd][-1] == self.orig_schema[hd][0]:
          return True
        else:
          return False
    except:
      return False

  def find_empty(self, field_string):
    fs = field_string.split('_')
    hd = fs[0]
    d = {}
    if isinstance(self.curr_schema[hd], dict):
      assert len(fs) == 2
      if isinstance(self.curr_schema[hd][fs[1]], list):
        d = self.curr_schema[hd][fs[1]][-1]
      else:
        d = self.curr_schema[hd][fs[1]]
    else:
      d = self.curr_schema[hd][0]

    f = []
    if isinstance(d, dict):
      for k, v in d.items():
        if v == '':
          f.append(k)
        elif isinstance(v, list):
          if v[-1] == '':
            f.append(k)

    return f

    # fs = field_string.split('_')
    # d = self.curr_schema
    # for k in fs[2:]:
    #   if isinstance(d[k], dict):
    #     d = d[k]
    #   elif isinstance(d[k], list):
    #     d = d[k][-1]
  def progress_percent(self):
    progress = total = 0
    for key, value in self.curr_schema.items():
      # print(key)
      try:
        if isinstance(self.curr_schema[key], dict):
          for k, v in self.curr_schema[key].items():
            # print(key, k)
            if isinstance(self.curr_schema[key][k], list):
            # print(fs, self.curr_schema[hd][fs[1]], self.orig_schema[hd][fs[1]])
            # print(self.curr_schema[hd][fs[1]][-1] == self.orig_schema[hd][fs[1]][0])
              if self.curr_schema[key][k][0] != self.orig_schema[key][k][0]:
                progress += 1
            else:
              if self.curr_schema[key][k] != '':
                progress += 1
            total += 1
        else:
          if self.curr_schema[key][0] != self.orig_schema[key][0]:
            progress += 1
          total += 1
      except:
        pass
    return progress * 100 / total 

  def choose_random_empty(self):
    empty_list = []
    for key, value in self.curr_schema.items():
      if key != 'Demographics':
        if isinstance(self.curr_schema[key], dict):
          for k, v in self.curr_schema[key].items():
            if isinstance(self.curr_schema[key][k], list):
              if self.curr_schema[key][k][0] == self.orig_schema[key][k][0]:
                empty_list.append('.'.join([key, k]))
            else:
              if self.curr_schema[key][k] == '':
                empty_list.append('.'.join([key, k]))
        else:
          if self.curr_schema[key][0] == self.orig_schema[key][0]:
            empty_list.append(key)
    print('All empty fields:', empty_list)
    return random.choice(empty_list)
