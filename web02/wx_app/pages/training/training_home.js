Page({

  data: {
    training_modes: ['分科练习', '综合练习'],
    subjects_array: ['微观经济学', '宏观经济学', '政治经济学'],
    select_modes: ['选择题', '名词解释', '简答题', '计算题', '论述题'],
    index: 0,
    subject_index: 0,
    mode_index: 0
  },

  bindPickerChange(e) {
    console.log('picker发送选择改变，携带值为', e.detail.value)
    this.setData({
      index: e.detail.value
    })
  },

})