import React from "react";
import { Controller, useForm } from "react-hook-form";
import { formFieldTypes } from "../lib/constants";
import Button from "./Button";
import Input from "./Input";
import styled, { css } from "styled-components";
import { sharedFlexCenter, sharedFlexSpaceBetween } from "../styles/global";

interface FormProps {
  formFields: any;
  row?: boolean;
  isFormRow?: boolean;
}

const FormController: React.FC<FormProps> = ({
  formFields,
  row,
  isFormRow,
}) => {
  const { control, handleSubmit, formState } = useForm(); //TODO: controller is used to register external component(i.e Input, dropdown) values to form.
  const { submit } = formFieldTypes;
  const { isSubmitting } = formState;

  return (
    <Form>
      <FormFieldContainer $row={isFormRow}>
        {formFields?.fields?.map(
          (formField: any, index: React.Key | null | undefined) => (
            <FieldContainer $row={isFormRow} key={index}>
              <Field $row={row}>
                <Label>{formField.label}</Label>
                {formField.defaultValue !== "undefined" && ( //Temporary approach. will be checked once api's available
                  <Controller
                    name={formField.name}
                    control={control}
                    defaultValue={formField.defaultValue}
                    render={({ field }) => (
                      <>
                        <Input
                          title={formField.name}
                          value={field.value ?? formField.defaultValue}
                          onChangeHandler={field.onChange}
                          type={formField.inputType}
                          inputStyle={formField.style}
                          required={formField.required && formField.required}
                          defaultValue={formField.defaultValue}
                          placeholder={formField.placeholder}
                          readOnly={formField.readOnly}
                          disabled={formField.disabled}
                          enableInputStyleWithValue={
                            formField?.enableInputStyleWithValue
                          }
                        />
                      </>
                    )}
                  />
                )}
              </Field>
            </FieldContainer>
          )
        )}
      </FormFieldContainer>
      <div>
        {formFields?.buttons?.map(
          (
            { name, type, onSubmitHandler, style }: any,
            index: React.Key | null | undefined
          ) => (
            <Button
              key={index}
              title={name}
              clickHandler={
                type === submit
                  ? handleSubmit(onSubmitHandler)
                  : onSubmitHandler
              }
              buttonStyle={style}
            />
          )
        )}{" "}
      </div>
    </Form>
  );
};

export default FormController;

const Form = styled.form`
  ${sharedFlexCenter}
  width:100%;
  flex-direction: column;
`;

const FlexRow = css`
  flex-wrap: wrap;
  flex-direction: row;
`;

const FormFieldContainer = styled.div<{ $row?: boolean }>`
  ${sharedFlexCenter}
  width:100%;
  flex-direction: column;
  ${(props) => props.$row && FlexRow}
`;
const FieldContainer = styled.div<{ $row?: boolean }>`
  ${sharedFlexCenter}
  width: ${(props) => (props.$row ? "40%" : "60%")};
  padding: 0 2rem;
`;

const Field = styled.div<{ $row?: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  margin-bottom: 1rem;
  width: 100%;
  ${(props) => props.$row && sharedFlexSpaceBetween}
`;

const Label = styled.label`
  font-weight: 600;
  font-family: Lato, sans-serif;
  font-size: 0.875rem;
  line-height: 1.25rem;
  margin-right: 1rem;
  text-transform: capitalize;
  width: max-content;
`;
