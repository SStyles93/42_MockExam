#include <unistd.h>

int	main(int argc, char **argv)
{
	int		arg;
	int		i;
	char	c;
	int		word_start;

	if (argc == 1)
		write(1, "\n", 1);
	arg = 1;
	while (arg < argc)
	{
		i = 0;
		while (argv[arg][i])
		{
			c = argv[arg][i];
			word_start = (i == 0 || argv[arg][i - 1] == ' '
					|| argv[arg][i - 1] == '\t');
			if (c >= 'A' && c <= 'Z')
				c += 32;
			if (word_start && c >= 'a' && c <= 'z')
				c -= 32;
			write(1, &c, 1);
			i++;
		}
		write(1, "\n", 1);
		arg++;
	}
	return (0);
}
