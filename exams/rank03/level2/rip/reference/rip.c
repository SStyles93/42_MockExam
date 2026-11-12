#include <unistd.h>

static int	is_balanced(char *s)
{
	int	open;

	open = 0;
	while (*s)
	{
		if (*s == '(')
			open++;
		else if (*s == ')')
		{
			if (!open)
				return (0);
			open--;
		}
		s++;
	}
	return (open == 0);
}

static void	solve(char *s, int len, int start, int left)
{
	int		i;
	char	saved;

	if (left == 0)
	{
		if (is_balanced(s))
		{
			write(1, s, len);
			write(1, "\n", 1);
		}
		return ;
	}
	i = start;
	while (i < len)
	{
		if (s[i] != ' ')
		{
			saved = s[i];
			s[i] = ' ';
			solve(s, len, i + 1, left - 1);
			s[i] = saved;
		}
		i++;
	}
}

int	main(int argc, char **argv)
{
	int	len;
	int	open;
	int	extra;

	if (argc != 2)
		return (1);
	len = 0;
	open = 0;
	extra = 0;
	while (argv[1][len])
	{
		if (argv[1][len] == '(')
			open++;
		else if (argv[1][len] == ')')
		{
			if (open)
				open--;
			else
				extra++;
		}
		len++;
	}
	solve(argv[1], len, 0, open + extra);
	return (0);
}
