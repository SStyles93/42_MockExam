#include <unistd.h>

int	main(int argc, char **argv)
{
	char	*s;
	int		first;

	if (argc == 2)
	{
		s = argv[1];
		first = 1;
		while (*s)
		{
			while (*s == ' ' || *s == '\t')
				s++;
			if (!*s)
				break ;
			if (!first)
				write(1, "   ", 3);
			while (*s && *s != ' ' && *s != '\t')
				write(1, s++, 1);
			first = 0;
		}
	}
	write(1, "\n", 1);
	return (0);
}
