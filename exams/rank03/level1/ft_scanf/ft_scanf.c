#include <stdarg.h>
#include <stdio.h>
#include <ctype.h>

/* Skips any amount of whitespace in the input. */
int	match_space(FILE *f)
{
	/* write your code here */
	(void)f;
	return (0);
}

/* Consumes c if it is the next input character. Returns 1 on success. */
int	match_char(FILE *f, char c)
{
	/* write your code here */
	(void)f;
	(void)c;
	return (0);
}

/* %c: reads one character into the next char * argument. Returns 1 on success. */
int	scan_char(FILE *f, va_list ap)
{
	/* write your code here */
	(void)f;
	(void)ap;
	return (0);
}

/* %d: reads a signed decimal integer into the next int * argument. */
int	scan_int(FILE *f, va_list ap)
{
	/* write your code here */
	(void)f;
	(void)ap;
	return (0);
}

/* %s: reads a sequence of non-whitespace characters into the next char *. */
int	scan_string(FILE *f, va_list ap)
{
	/* write your code here */
	(void)f;
	(void)ap;
	return (0);
}

int	match_conv(FILE *f, const char **format, va_list ap)
{
	switch (**format)
	{
		case 'c':
			return (scan_char(f, ap));
		case 'd':
			match_space(f);
			return (scan_int(f, ap));
		case 's':
			match_space(f);
			return (scan_string(f, ap));
		default:
			return (-1);
	}
}

int	ft_vfscanf(FILE *f, const char *format, va_list ap)
{
	int	nconv;
	int	c;

	nconv = 0;
	c = fgetc(f);
	if (c == EOF)
		return (EOF);
	ungetc(c, f);
	while (*format)
	{
		if (*format == '%')
		{
			format++;
			if (match_conv(f, &format, ap) != 1)
				break ;
			nconv++;
		}
		else if (isspace(*format))
		{
			if (match_space(f) == -1)
				break ;
		}
		else if (match_char(f, *format) != 1)
			break ;
		format++;
	}
	if (ferror(f))
		return (EOF);
	return (nconv);
}

int	ft_scanf(const char *format, ...)
{
	va_list	ap;
	int		ret;

	va_start(ap, format);
	ret = ft_vfscanf(stdin, format, ap);
	va_end(ap);
	return (ret);
}
