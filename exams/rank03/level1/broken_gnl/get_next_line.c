#include "get_next_line.h"

static size_t	gnl_strlen(const char *s)
{
	size_t	len;

	len = 0;
	while (s && s[len])
		len++;
	return (len);
}

static char	*gnl_strchr(char *s, char c)
{
	while (*s != c)
		s++;
	if (*s == c)
		return (s);
	return (NULL);
}

/* Appends the first n bytes of src to *line. Frees *line on failure. */
static int	append(char **line, const char *src, size_t n)
{
	size_t	old;
	size_t	i;
	char	*joined;

	old = gnl_strlen(*line);
	joined = malloc(old + n + 1);
	if (!joined)
	{
		free(*line);
		*line = NULL;
		return (0);
	}
	i = 0;
	while (i < old)
	{
		joined[i] = (*line)[i];
		i++;
	}
	i = 0;
	while (i < n)
	{
		joined[old + i] = src[i];
		i++;
	}
	joined[old + n] = '\0';
	*line = joined;
	return (1);
}

/* Removes the first n bytes of buf and keeps the rest. */
static void	shift(char *buf, size_t n)
{
	size_t	i;

	i = 0;
	while (buf[n + i])
	{
		buf[i] = buf[n + i];
		i++;
	}
}

char	*get_next_line(int fd)
{
	static char	buf[BUFFER_SIZE + 1];
	char		*line;
	char		*nl;
	ssize_t		r;

	line = NULL;
	while (1)
	{
		nl = gnl_strchr(buf, '\n');
		if (nl)
		{
			if (!append(&line, buf, nl - buf))
				return (NULL);
			shift(buf, nl - buf + 1);
			return (line);
		}
		if (buf[0] && !append(&line, buf, gnl_strlen(buf)))
			return (NULL);
		buf[0] = '\0';
		r = read(fd, buf, BUFFER_SIZE);
		if (r <= 0)
		{
			if (r < 0)
			{
				free(line);
				return (NULL);
			}
			return (line);
		}
		buf[r] = '\0';
	}
}
