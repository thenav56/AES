from django import template


def timeDelta(td):
    if td is not None:
        total_seconds = int(td.total_seconds())
        time = []
        if total_seconds > 3600:
            hours = int(total_seconds / 3600)
            minutes = int((total_seconds % 3600) / 60)
            seconds = int((total_seconds % (60)))
            if hours > 0:
                time.append('{} hours'.format(hours))
            if minutes > 0:
                time.append('{} min'.format(minutes))
            if seconds > 0:
                time.append('{} sec'.format(seconds))
            return ' '.join(time)
        elif total_seconds > 60:
            minutes = int((total_seconds / 60))
            seconds = (total_seconds % 60)
            if minutes > 0:
                time.append('{} min'.format(minutes))
            if seconds > 0:
                time.append('{} sec'.format(seconds))
            return ' '.join(time)
        else:
            return '{} sec'.format(total_seconds)
    return '0 sec'


register = template.Library()
register.filter('timeDelta', timeDelta)
