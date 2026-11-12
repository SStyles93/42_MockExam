#include <unistd.h>

int	main(int argc, char **argv)
{
	char	*s;
	int		end;
	int		start;

	if (argc == 2)
	{
		s = argv[1];
		end = 0;
		while (s[end])
			end++;
		end--;
		while (end >= 0 && (s[end] == ' ' || s[end] == '\t'))
			end--;
		start = end;
		while (start >= 0 && s[start] != ' ' && s[start] != '\t')
			start--;
		write(1, s + start + 1, end - start);
	}
	write(1, "\n", 1);
	return (0);
}
