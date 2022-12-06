from django import template

register = template.Library()


UNWANTED_WORDS = ('маск', 'маска', 'маску', 'маском', 'маске',
                  'футбол', 'футбола', 'футболу', 'футболом', 'футболе',
                  'конкурс', 'конкурса', 'конкурсу', 'конкурсом', 'конкурсе',
                  'конкурсы', 'конкурсов', 'конкурсам', 'конкурсами', 'конкурсах')


@register.filter()
def censor(text, symbol='*'):
    """
    text: текст, к которому нужно применить фильтр
    """
    try:
        text_list = text.split()
        for i, word in enumerate(text_list):
            word = word.lower().replace('(', '').replace(')', '').\
                replace(',', '').replace('.', '').replace('-', '').replace('!', '').\
                replace('?', '').replace('\'', '').replace('\"', '')
            if word in UNWANTED_WORDS:
                text_list[i] = text_list[i].replace(word[1:], symbol * (len(word) - 1), 1)
        return f'{" ".join(text_list)}'
    except AttributeError:
        return 'Цензура может быть применена только к тексту'
