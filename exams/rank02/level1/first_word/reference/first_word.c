#include <unistd.h>

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t');
}

int	main(int argc, char **argv)
{
	char	*s;

	if (argc == 2)
	{
		s = argv[1];
		while (is_blank(*s))
			s++;
		while (*s && !is_blank(*s))
			write(1, s++, 1);
	}
	write(1, "\n", 1);
	return (0);
}
