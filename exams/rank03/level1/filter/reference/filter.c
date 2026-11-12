#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int	fail(char *data)
{
	free(data);
	perror("Error");
	return (1);
}

static void	replace(char *data, size_t len, char *s, size_t slen)
{
	size_t	i;
	size_t	j;

	i = 0;
	while (i + slen <= len)
	{
		j = 0;
		while (j < slen && data[i + j] == s[j])
			j++;
		if (j == slen)
		{
			while (j--)
				data[i + j] = '*';
			i += slen;
		}
		else
			i++;
	}
}

int	main(int argc, char **argv)
{
	char	*data;
	char	*tmp;
	size_t	len;
	size_t	cap;
	ssize_t	r;

	if (argc != 2 || !argv[1][0])
		return (1);
	cap = 4096;
	len = 0;
	data = malloc(cap);
	if (!data)
		return (fail(NULL));
	while (1)
	{
		if (len == cap)
		{
			cap *= 2;
			tmp = realloc(data, cap);
			if (!tmp)
				return (fail(data));
			data = tmp;
		}
		r = read(0, data + len, cap - len);
		if (r < 0)
			return (fail(data));
		if (r == 0)
			break ;
		len += r;
	}
	replace(data, len, argv[1], strlen(argv[1]));
	write(1, data, len);
	free(data);
	return (0);
}
