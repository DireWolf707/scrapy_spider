from itemadapter import ItemAdapter

class CoursePipeline:
    def process_item(self, item, spider):
        spider.tel_bot.send_message(
            text=self.format_message(item),
            chat_id = spider.user_id,
            parse_mode = 'HTML')
        return item

    def format_message(self, item):
        item = ItemAdapter(item)
        msg = []
        for k,v in item.items():
            if k == 'links':
                msg.append( ', '.join( list( map(lambda x: f'<a href="{x}">Mirror Link</a>', v) ) ) )
            else:
                msg.append(f'<b>{v}</b>')
        return '\n'.join(msg)
