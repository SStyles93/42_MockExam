#include <unistd.h>

int	main(int argc, char **argv)
{
	char	*s;
	char	c;

	if (argc == 2)
	{
		s = argv[1];
		while (*s)
		{
			c = *s;
			if (c >= 'a' && c <= 'z')
				c = 'a' + 'z' - c;
			else if (c >= 'A' && c <= 'Z')
				c = 'A' + 'Z' - c;
			write(1, &c, 1);
			s++;
		}
	}
	write(1, "\n", 1);
	return (0);
}
