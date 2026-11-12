#include <unistd.h>

static int	is_blank(char c)
{
	return (c == ' ' || c == '\t' || c == '\0');
}

int	main(int argc, char **argv)
{
	int		arg;
	int		i;
	char	c;

	if (argc == 1)
		write(1, "\n", 1);
	arg = 1;
	while (arg < argc)
	{
		i = 0;
		while (argv[arg][i])
		{
			c = argv[arg][i];
			if (c >= 'A' && c <= 'Z')
				c += 32;
			if (c >= 'a' && c <= 'z' && is_blank(argv[arg][i + 1]))
				c -= 32;
			write(1, &c, 1);
			i++;
		}
		write(1, "\n", 1);
		arg++;
	}
	return (0);
}
